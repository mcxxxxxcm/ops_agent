from langchain_openai import ChatOpenAI
from datetime import datetime
from typing import Optional, List, Dict, Any
from rich.console import Console
from pathlib import Path
import asyncio

from src.tools import (
    read_log_file,
    analyze_error,
    generate_report,
    ask_user,
)
from config.settings import settings
from config.prompts import ANALYSIS_PROMPT

console = Console()


class DiagnosisAgent:
    """智能运维故障排查助手

    使用确定性流程的诊断系统。
    流程：读取日志 -> 分析错误（交互式）-> 生成报告
    """

    def __init__(
            self,
            model: str = None,
            temperature: float = None,
            max_error_lines: int = None,
            parallel_analysis: bool = None,
    ):
        """初始化诊断智能体

        Args:
            model: LLM模型名称，默认从配置读取
            temperature: 生成温度，默认从配置读取
            max_error_lines: 最大读取的ERROR日志数量，默认从配置读取
            parallel_analysis: 是否并行分析错误（更快，但无交互），默认从配置读取
        """
        self.model = model or settings.llm_model
        self.temperature = temperature or settings.llm_temperature
        self.max_error_lines = max_error_lines or settings.max_error_lines
        self.parallel_analysis = parallel_analysis if parallel_analysis is not None else settings.parallel_analysis

        # 初始化LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=settings.llm_max_tokens,
            api_key=settings.glm_api_key,
            base_url=settings.glm_api_base,
            stream_usage=True,
        )

        # 存储诊断结果
        self.diagnosis_results: List[Dict[str, Any]] = []

    async def diagnose(self, log_file: str) -> str:
        """执行故障诊断（确定性流程）

        Args:
            log_file: 日志文件路径

        Returns:
            诊断结果摘要
        """
        console.print("[cyan]📖 步骤1: 读取日志文件...[/cyan]")

        log_entries = await read_log_file.ainvoke({
            "file_path": log_file,
            "max_lines": self.max_error_lines,
        })

        if not log_entries:
            console.print("[yellow]⚠️ 未发现 ERROR 级别日志[/yellow]")
            return "未发现错误日志"

        console.print(f"[green]✓ 读取到 {len(log_entries)} 条错误日志[/green]\n")

        # 步骤2: 分析错误
        console.print("[cyan]🔍 步骤2: 分析错误日志...[/cyan]")

        if self.parallel_analysis:
            # 并行模式：同时分析所有错误（更快）
            console.print("[dim]并行分析模式（更快）...[/dim]\n")
            self.diagnosis_results = await self._parallel_analyze(log_entries)
        else:
            # 交互模式：逐条分析（可随时停止）
            console.print("[dim]交互分析模式（可随时停止）...[/dim]\n")
            self.diagnosis_results = await self._interactive_analyze(log_entries)

        # 步骤3: 生成报告
        console.print("\n[cyan]📝 步骤3: 生成诊断报告...[/cyan]")

        report_path = await generate_report.ainvoke({
            "analysis_results": self.diagnosis_results,
        })

        return report_path

    async def chat(self, message: str) -> str:
        """简单对话模式

        Args:
            message: 用户消息

        Returns:
            智能体回复
        """
        # 直接使用 LLM 进行简单对话，强制使用中文
        from langchain_core.messages import HumanMessage

        # 添加中文提示
        prompt = f"{message}\n\n请用中文回复。"

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content

    async def diagnose_with_path(self, log_path: str) -> str:
        """诊断指定路径的日志文件

        Args:
            log_path: 日志文件的完整路径

        Returns:
            诊断结果
        """
        # 验证路径
        path = Path(log_path)
        if not path.exists():
            raise FileNotFoundError(f"日志文件不存在: {log_path}")

        if not path.is_file():
            raise ValueError(f"路径不是文件: {log_path}")

        # 执行诊断
        return await self.diagnose(str(path.absolute()))

    async def _interactive_analyze(self, log_entries):
        """交互式分析（逐条分析，可随时停止）

        Args:
            log_entries: 日志条目列表

        Returns:
            分析结果列表
        """
        results = []

        for i, entry in enumerate(log_entries, 1):
            console.print(f"\n[yellow]--- 分析第 {i}/{len(log_entries)} 条错误 ---[/yellow]")

            analysis = await analyze_error.ainvoke({
                "error_log": entry,
            })

            results.append({
                "entry": entry,
                "analysis": analysis,
            })

            if i < len(log_entries):
                continue_analysis = await ask_user.ainvoke({
                    "question": f"已分析 {i}/{len(log_entries)} 条错误，是否继续分析剩余 {len(log_entries) - i} 条？（输入 y 继续，n 停止）",
                })

                if continue_analysis in ["n", "no", "否"]:
                    console.print("[yellow]⚠️ 用户选择停止分析[/yellow]")
                    break

        return results

    async def _parallel_analyze(self, log_entries):
        """并行分析（同时分析所有错误，更快）

        Args:
            log_entries: 日志条目列表

        Returns:
            分析结果列表
        """
        import asyncio

        async def analyze_single(entry):
            return await analyze_error.ainvoke({
                "error_log": entry,
            })

        console.print(f"[dim]正在并行分析 {len(log_entries)} 条错误...[/dim]")

        tasks = [analyze_single(entry) for entry in log_entries]
        analyses = await asyncio.gather(*tasks)

        results = []
        for entry, analysis in zip(log_entries, analyses):
            results.append({
                "entry": entry,
                "analysis": analysis,
            })

        console.print(f"[green]✓ 并行分析完成[/green]")
        return results