from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class LogEntry(BaseModel):
    """日志条目数据模型

    表示单条日志记录，包含时间戳、级别、消息等信息
    """

    timestamp: datetime = Field(
        ...,
        description="日志时间戳"
    )
    level: LogLevel = Field(
        ...,
        description="日志级别"
    )
    message: str = Field(
        ...,
        description="日志消息内容"
    )
    source: str = Field(
        default="unknown",
        description="日志来源（模块/类名）"
    )
    line_number: int = Field(
        default=0,
        description="原始文件中的行号"
    )
    stack_trace: Optional[str] = Field(
        default=None,
        description="堆栈跟踪信息（如有）"
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="额外上下文信息"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self) -> dict:
        """转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "line_number": self.line_number,
            "stack_trace": self.stack_trace,
            "context": self.context,
        }