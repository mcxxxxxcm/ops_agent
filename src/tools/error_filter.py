from langchain_core.tools import tool
from typing import List, Dict, Any
from rich.console import Console

console = Console()


@tool
def filter_error_logs(
        log_entries: List[Dict[str, Any]],
        level: str = "ERROR"
) -> List[Dict[str, Any]]:
    """从日志条目中筛选指定级别的日志

    Args:
        log_entries: 日志条目列表
        level: 要筛选的日志级别，默认为 ERROR
               支持：DEBUG, INFO, WARN, ERROR, FATAL

    Returns:
        筛选后的日志条目列表
    """
    filtered = []
    target_level = level.upper()

    for entry in log_entries:
        entry_level = entry.get('level', '').upper()
        if entry_level == target_level:
            filtered.append(entry)

    # 显示筛选结果
    if filtered:
        console.print(f"\n[yellow]🔍 筛选出[/yellow] {len(filtered)} [yellow]条 {level} 级别日志[/yellow]")
        # 显示前 3 条错误预览
        for i, entry in enumerate(filtered[:3], 1):
            msg = entry.get('message', '')[:80]
            console.print(f"  [dim]{i}. {msg}[/dim]")
        if len(filtered) > 3:
            console.print(f"  [dim]... 还有 {len(filtered) - 3} 条[/dim]")

    return filtered