import aiofiles
from langchain_core.tools import tool
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from rich.console import Console

from config.settings import settings
from config.prompts import DIAGNOSIS_TEMPLATE, ERROR_SECTION_TEMPLATE

console = Console()


@tool
async def generate_report(
        analysis_results: List[Dict[str, Any]],
        output_filename: str = "diagnosis_report.md"
) -> str:
    """异步生成诊断报告

    Args:
        analysis_results: 分析结果列表
        output_filename: 报告文件名，默认为 diagnosis_report.md

    Returns:
        生成的报告文件完整路径
    """
    console.print(f"\n[cyan]📝 正在生成诊断报告...[/cyan]")

    # 构建错误部分
    error_sections = []
    for idx, result in enumerate(analysis_results, 1):
        error_log = result.get('error_log', {})
        analysis = result.get('analysis', '')

        # 堆栈跟踪部分
        stack_trace_section = ""
        if error_log.get('stack_trace'):
            stack_trace_section = f"""### 堆栈跟踪
```
{error_log['stack_trace']}
```
"""

        # 构建单个错误部分
        error_section = ERROR_SECTION_TEMPLATE.format(
            index=idx,
            timestamp=error_log.get('timestamp', '未知'),
            source=error_log.get('source', '未知'),
            level=error_log.get('level', 'ERROR'),
            message=error_log.get('message', ''),
            stack_trace_section=stack_trace_section,
            analysis=analysis,
        )
        error_sections.append(error_section)

    # 生成摘要
    summary = f"本次诊断共分析 {len(analysis_results)} 个错误。建议优先处理严重程度高的错误，并按照分析建议进行修复。"

    # 构建完整报告
    report_content = DIAGNOSIS_TEMPLATE.format(
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_errors=len(analysis_results),
        error_sections='\n'.join(error_sections),
        summary=summary,
    )

    # 获取输出路径
    output_path = settings.get_output_path(output_filename)
    
    # 修复路径重复问题：如果路径包含重复的 output/output，则修正
    path_str = str(output_path)
    if "output\\output\\" in path_str or "output/output/" in path_str:
        # 替换重复的 output
        path_str = path_str.replace("output\\output\\", "output\\").replace("output/output/", "output/")
        output_path = Path(path_str)
    
    # 确保目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 异步写入文件
    async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
        await f.write(report_content)

    # 显示生成结果
    console.print(f"\n[green bold]✅ 报告已生成：[/green bold] [link=file://{output_path}]{output_path}[/link]")

    return str(output_path.absolute())
