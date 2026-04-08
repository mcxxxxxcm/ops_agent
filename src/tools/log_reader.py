from langchain_core.tools import tool
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
from rich.console import Console
from src.parsers.multi_format_parser import MultiFormatParser

console = Console()


@tool
async def read_log_file(
    file_path: str,
    max_lines: int = 100,
    only_errors: bool = True,
    error_keywords: Optional[List[str]] = None,
    analyze_count: int = 5
) -> List[Dict[str, Any]]:
    """异步读取指定路径的日志文件 - 优化版（直接返回ERROR日志）
    
    性能优化 + 一步到位：
    1. 默认只读取包含 ERROR/EXCEPTION/WARN 的关键行
    2. 支持限制最大读取行数
    3. 直接返回筛选后的错误日志
    4. 支持指定本次分析的数量（默认5条，避免分析太多）

    Args:
        file_path: 日志文件的完整路径
        max_lines: 最大读取行数，默认10条错误
        only_errors: 是否只读取错误级别日志，默认True（固定为True）
        error_keywords: 自定义错误关键词列表，默认 ["ERROR", "EXCEPTION", "FATAL", "WARN", "WARNING"]
        analyze_count: 本次要分析的错误数量，默认5条（避免分析太多导致超时）

    Returns:
        错误日志条目列表，每个条目包含时间戳、级别、消息等信息
    """
    path = Path(file_path)

    # 验证路径
    if not path.exists():
        raise FileNotFoundError(f"日志文件不存在：{file_path}")

    if not path.is_file():
        raise ValueError(f"路径不是文件：{file_path}")

    # 获取文件大小
    file_size = path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    # 显示读取状态
    console.print(f"\n[blue]📄 正在读取日志文件：[/blue] {file_path}")
    console.print(f"[dim]文件大小: {file_size_mb:.2f} MB[/dim]")

    # 固定只读取错误级别
    only_errors = True
    
    # 默认错误关键词（只筛选ERROR级别）
    if error_keywords is None:
        error_keywords = ["ERROR", "EXCEPTION", "FATAL"]
    
    # 编译正则表达式用于快速匹配
    error_pattern = re.compile(
        '|'.join(re.escape(kw) for kw in error_keywords),
        re.IGNORECASE
    )
    
    # 使用多格式解析器
    parser = MultiFormatParser()
    
    # 高性能读取：只读取关键行
    filtered_entries = []
    lines_read = 0
    matched_lines = 0
    
    # 对于大文件，使用流式读取
    if file_size_mb > 1:
        console.print(f"[yellow]⚡ 大文件检测 ({file_size_mb:.1f}MB)，启用优化读取模式[/yellow]")
        
        # 只读取匹配关键词的行
        async for line in _async_file_lines(path):
            lines_read += 1
            
            # 快速预过滤：跳过明显无关的行
            if only_errors and not error_pattern.search(line):
                continue
            
            # 解析日志行
            entry = parser.parse(line, lines_read)
            if entry:
                filtered_entries.append(entry)
                matched_lines += 1
            
            # 达到最大匹配数就停止
            if matched_lines >= max_lines:
                break
    else:
        # 小文件：直接解析所有行
        entries = await parser.parse_file_async(file_path)
        lines_read = len(entries)  # 记录读取的行数
        
        if only_errors:
            # 过滤出错误级别
            for entry in entries:
                if entry.level.value in ["ERROR", "FATAL"]:
                    filtered_entries.append(entry)
                    matched_lines += 1
                    if matched_lines >= max_lines:
                        break
        else:
            filtered_entries = entries[:max_lines]
            matched_lines = len(filtered_entries)

    # 显示读取结果
    console.print(f"[green]✓ 已读取[/green] {min(matched_lines, max_lines)} [green]条关键日志[/green] (共扫描 {lines_read} 行)")
    
    # 强制限制返回数量
    filtered_entries = filtered_entries[:max_lines]
    
    # 直接返回筛选后的结果（最多 max_lines 条）
    result = [entry.to_dict() for entry in filtered_entries]
    
    # 显示筛选出的错误预览
    if result:
        console.print(f"\n[yellow]🔍 筛选出 {len(result)} 条 ERROR 级别日志：[/yellow]")
        for i, entry in enumerate(result[:5], 1):
            msg = entry.get('message', '')[:60]
            console.print(f"  {i}. {msg}")
        if len(result) > 5:
            console.print(f"  ... 还有 {len(result) - 5} 条")
    
    return result


async def _async_file_lines(file_path: Path, encoding: str = 'utf-8'):
    """异步逐行读取文件"""
    import aiofiles
    
    async with aiofiles.open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        async for line in f:
            yield line.rstrip('\n')