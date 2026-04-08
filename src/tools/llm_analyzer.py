from langchain_core.tools import tool
from typing import Dict, Any, Optional
from datetime import datetime
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config.settings import settings
from config.prompts import ANALYSIS_PROMPT

console = Console()


@tool
async def analyze_error(
        error_log: Dict[str, Any],
        context: Optional[str] = None
) -> Dict[str, Any]:
    """异步使用 LLM 分析单个错误日志，支持流式输出

    Args:
        error_log: 错误日志条目，包含 timestamp, level, message 等字段
        context: 额外的上下文信息（可选）

    Returns:
        包含分析结果的字典，包括错误类型、原因、建议等
    """
    # 根据 LLM 提供商选择配置
    if settings.llm_provider == "zhipu":
        api_key = settings.glm_api_key
        base_url = settings.glm_api_base
    elif settings.llm_provider == "openai":
        api_key = settings.openai_api_key
        base_url = settings.openai_api_base
    else:
        api_key = settings.glm_api_key
        base_url = settings.glm_api_base
    
    # 初始化 LLM（不启用流式，减少开销）
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=api_key,
        base_url=base_url,
        streaming=True,  # 流式输出
    )

    # 构建提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的运维故障诊断专家。请分析错误并提供结构化的诊断结果。"),
        ("user", ANALYSIS_PROMPT),
    ])

    # 准备输入数据
    stack_trace_str = ""
    if error_log.get('stack_trace'):
        stack_trace_str = f"\n堆栈跟踪:\n```\n{error_log['stack_trace']}\n```"

    context_str = f"\n上下文信息:\n{context}" if context else ""

    # 显示错误信息
    console.print(f"\n[yellow bold]🔍 分析错误 #[/yellow bold]")
    console.print(f"  [cyan]时间:[/cyan] {error_log.get('timestamp', '未知')}")
    console.print(f"  [cyan]来源:[/cyan] {error_log.get('source', '未知')}")
    console.print(f"  [cyan]消息:[/cyan] {error_log.get('message', '')[:100]}")

    # 流式调用 LLM
    console.print(f"\n[green]✨ 分析结果:[/green]")

    chain = prompt | llm
    full_response = ""

    # 计时开始
    start_time = time.time()
    first_token_time = None

    # 流式输出
    async for chunk in chain.astream({
        "timestamp": error_log.get('timestamp', '未知'),
        "level": error_log.get('level', 'ERROR'),
        "source": error_log.get('source', '未知'),
        "message": error_log.get('message', ''),
        "stack_trace": stack_trace_str,
        "context": context_str,
    }):
        # 记录首 token 时间
        if first_token_time is None and hasattr(chunk, 'content') and chunk.content:
            first_token_time = time.time()
            ttft = first_token_time - start_time
            console.print(f"\n[dim]⏱️ 首 token 延迟: {ttft:.2f}s[/dim]")

        if hasattr(chunk, 'content') and chunk.content:
            full_response += chunk.content
            console.print(chunk.content, end="", markup=False)

    total_time = time.time() - start_time
    console.print(f"\n[dim]⏱️ 总响应时间: {total_time:.2f}s[/dim]")

    # 生成唯一 ID
    log_entry_id = f"{error_log.get('source', 'unknown')}_{error_log.get('line_number', 0)}"

    # 返回结构化结果
    return {
        "log_entry_id": log_entry_id,
        "error_log": error_log,
        "analysis": full_response,
        "analyzed_at": datetime.now().isoformat(),
    }