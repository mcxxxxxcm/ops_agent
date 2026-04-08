from abc import ABC, abstractmethod
from typing import Optional, List

from src.models.log_entry import LogEntry


class BaseParser(ABC):
    """日志解析器基类

    定义日志解析器的标准接口，支持异步操作
    """

    @abstractmethod
    def parse(self, line: str, line_number: int = 0) -> Optional[LogEntry]:
        """解析单行日志（同步方法）

        Args:
            line: 日志行内容
            line_number: 行号（用于错误定位）

        Returns:
            解析后的LogEntry对象，解析失败返回None
        """
        pass

    async def parse_file_async(self, file_path: str) -> List[LogEntry]:
        """异步解析整个日志文件

        Args:
            file_path: 日志文件路径

        Returns:
            解析后的LogEntry列表
        """
        import aiofiles
        from pathlib import Path

        entries = []
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"日志文件不存在: {file_path}")

        # 异步读取文件
        async with aiofiles.open(path, 'r', encoding='utf-8', errors='ignore') as f:
            line_num = 0
            async for line in f:
                line_num += 1
                line = line.strip()
                if not line:
                    continue

                entry = self.parse(line, line_num)
                if entry:
                    entries.append(entry)

        return entries

    def parse_file(self, file_path: str) -> List[LogEntry]:
        """同步解析整个日志文件（保留兼容性）

        Args:
            file_path: 日志文件路径

        Returns:
            解析后的LogEntry列表
        """
        from pathlib import Path

        entries = []
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"日志文件不存在: {file_path}")

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                entry = self.parse(line, line_num)
                if entry:
                    entries.append(entry)

        return entries