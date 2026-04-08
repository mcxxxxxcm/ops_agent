from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from .analysis_result import AnalysisResult


class DiagnosisReport(BaseModel):
    """诊断报告数据模型

    表示完整的诊断报告，包含多个分析结果
    """

    report_id: str = Field(
        ...,
        description="报告唯一标识"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="报告生成时间"
    )
    log_file: str = Field(
        ...,
        description="分析的日志文件路径"
    )
    total_errors: int = Field(
        default=0,
        description="日志中的错误总数"
    )
    analyzed_errors: int = Field(
        default=0,
        description="已分析的错误数量"
    )
    results: list[AnalysisResult] = Field(
        default_factory=list,
        description="分析结果列表"
    )
    summary: Optional[str] = Field(
        default=None,
        description="报告摘要"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def add_result(self, result: AnalysisResult) -> None:
        """添加分析结果

        Args:
            result: 分析结果对象
        """
        self.results.append(result)
        self.analyzed_errors = len(self.results)

    def to_dict(self) -> dict:
        """转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "log_file": self.log_file,
            "total_errors": self.total_errors,
            "analyzed_errors": self.analyzed_errors,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
        }