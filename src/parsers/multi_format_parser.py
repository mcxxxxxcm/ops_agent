from typing import Optional, List

from .base import BaseParser
from .regex_parser import RegexParser
from src.models.log_entry import LogEntry


class MultiFormatParser(BaseParser):
    """多格式日志解析器（组合模式）

    内部维护多个解析器，依次尝试解析，直到成功。
    这能处理包含多种格式混合的日志文件。
    """

    def __init__(self):
        """初始化多格式解析器"""
        self.parsers: List[BaseParser] = [
            RegexParser(),
        ]

    def add_parser(self, parser: BaseParser) -> None:
        """添加新的解析器

        Args:
            parser: 解析器实例
        """
        self.parsers.append(parser)

    def parse(self, line: str, line_number: int = 0) -> Optional[LogEntry]:
        """解析单行日志

        依次尝试所有解析器，返回第一个成功的结果

        Args:
            line: 日志行内容
            line_number: 行号

        Returns:
            解析后的LogEntry对象，所有解析器都失败返回None
        """
        for parser in self.parsers:
            try:
                entry = parser.parse(line, line_number)
                if entry:
                    return entry
            except Exception:
                # 解析失败，尝试下一个解析器
                continue

        return None