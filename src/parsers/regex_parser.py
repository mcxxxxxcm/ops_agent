import re
from datetime import datetime
from typing import Optional

from .base import BaseParser
from src.models.log_entry import LogEntry, LogLevel


class RegexParser(BaseParser):
    """基于正则表达式的日志解析器

    支持多种常见日志格式：
    - 标准格式: 2024-01-01 12:00:00 ERROR [module] message
    - Java格式: 2024-01-01 12:00:00,000 ERROR [main] com.example.Class - message
    - 简化格式: [ERROR] message
    """

    # 预编译的正则模式列表（按优先级排序）
    PATTERNS = [
        # 标准格式: 2024-01-01 12:00:00 ERROR [module] message
        re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\s+'
            r'\[(?P<source>[^\]]+)\]\s+'
            r'(?P<message>.+)'
        ),
        # Java格式: 2024-01-01 12:00:00,000 ERROR [main] com.example.Class - message
        re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s+'
            r'(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\s+'
            r'\[(?P<thread>[^\]]+)\]\s+'
            r'(?P<source>[\w.]+)\s+-\s+'
            r'(?P<message>.+)'
        ),
        # 简化格式: ERROR 2024-01-01 12:00:00 message
        re.compile(
            r'(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\s+'
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<message>.+)'
        ),
        # 最简格式: [ERROR] message
        re.compile(
            r'\[(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\]\s+'
            r'(?P<message>.+)'
        ),
    ]

    def parse(self, line: str, line_number: int = 0) -> Optional[LogEntry]:
        """解析单行日志

        Args:
            line: 日志行内容
            line_number: 行号

        Returns:
            解析后的LogEntry对象，解析失败返回None
        """
        # 尝试匹配各种格式
        for pattern in self.PATTERNS:
            match = pattern.match(line.strip())
            if match:
                return self._create_entry(match, line_number)

        # 如果都不匹配，作为纯消息处理（默认INFO级别）
        if line.strip():
            return LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                message=line.strip(),
                source="unknown",
                line_number=line_number,
            )

        return None

    def _create_entry(self, match: re.Match, line_number: int) -> LogEntry:
        """从正则匹配结果创建LogEntry

        Args:
            match: 正则匹配对象
            line_number: 行号

        Returns:
            LogEntry对象
        """
        groups = match.groupdict()

        # 解析时间戳
        timestamp_str = groups.get('timestamp', '')
        timestamp = self._parse_timestamp(timestamp_str)

        # 规范化日志级别
        level_str = groups.get('level', 'INFO').upper()
        if level_str == 'WARNING':
            level_str = 'WARN'
        level = LogLevel(level_str)

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=groups.get('message', ''),
            source=groups.get('source', groups.get('thread', 'unknown')),
            line_number=line_number,
        )

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """解析时间戳字符串

        Args:
            timestamp_str: 时间戳字符串

        Returns:
            datetime对象
        """
        if not timestamp_str:
            return datetime.now()

        # 支持的时间格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S,%f',
            '%d/%b/%Y:%H:%M:%S %z',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        # 解析失败，返回当前时间
        return datetime.now()