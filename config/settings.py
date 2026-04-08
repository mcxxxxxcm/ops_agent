from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # LLM 提供商配置
    llm_provider: Literal["openai", "zhipu", "anthropic"] = Field(
        default="zhipu",
        description="LLM 提供商：openai, zhipu(智谱), anthropic"
    )
    
    # LLM 通用配置
    llm_model: str = Field(
        default="",
        description="LLM 模型名称"
    )
    llm_temperature: float = Field(
        default=0.1,
        ge=0,
        le=1,
        description="生成温度，越低越确定"
    )
    llm_max_tokens: int = Field(
        default=2000,
        description="最大 token 数"
    )
    
    # OpenAI 配置
    openai_api_key: str = Field(
        default="",
        description="OpenAI API 密钥"
    )
    openai_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API 基础 URL"
    )
    
    # 智谱 AI 配置
    glm_api_key: str = Field(
        default="",
        description="智谱 API 密钥"
    )
    glm_api_base: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4/",
        description="智谱 API 基础 URL"
    )
    
    # 日志配置
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="日志级别"
    )
    log_file: str = Field(
        default="logs/ops_agent.log",
        description="日志文件路径"
    )
    
    # Agent 配置
    max_iterations: int = Field(
        default=15,
        description="Agent 最大迭代次数"
    )
    timeout: int = Field(
        default=300,
        description="超时时间（秒）"
    )
    max_error_lines: int = Field(
        default=10,
        description="最大读取的ERROR日志数量"
    )
    parallel_analysis: bool = Field(
        default=False,
        description="是否并行分析错误（更快，但无交互）"
    )
    
    # 输出配置
    output_dir: str = Field(
        default="output",
        description="输出目录"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }
    
    def get_output_path(self, filename: str) -> Path:
        """获取输出文件的完整路径"""
        # 使用当前工作目录作为项目根目录
        output_dir = Path.cwd() / "output"
            
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / filename


# 全局配置实例
settings = Settings()
