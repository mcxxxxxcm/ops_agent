from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AnalysisResult(BaseModel):
    """分析结果数据模型

    表示单条错误日志的分析结果
    """

    log_entry_id: str = Field(
        ...,
        description="对应日志条目的唯一标识"
    )
    error_type: str = Field(
        ...,
        description="错误类型分类"
    )
    root_cause: str = Field(
        ...,
        description="根本原因分析"
    )
    severity: str = Field(
        ...,
        description="严重程度：低/中/高/严重"
    )
    affected_components: list[str] = Field(
        default_factory=list,
        description="受影响的系统组件"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="修复建议列表"
    )
    related_docs: list[str] = Field(
        default_factory=list,
        description="相关文档或参考链接"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="分析置信度分数（0-1）"
    )
    analysis_time: datetime = Field(
        default_factory=datetime.now,
        description="分析时间"
    )
    raw_analysis: Optional[str] = Field(
        default=None,
        description="LLM原始分析文本"
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
            "log_entry_id": self.log_entry_id,
            "error_type": self.error_type,
            "root_cause": self.root_cause,
            "severity": self.severity,
            "affected_components": self.affected_components,
            "recommendations": self.recommendations,
            "related_docs": self.related_docs,
            "confidence_score": self.confidence_score,
            "analysis_time": self.analysis_time.isoformat(),
            "raw_analysis": self.raw_analysis,
        }