from pathlib import Path
from typing import Optional


def validate_file_path(file_path: str) -> bool:
    """验证文件路径是否有效

    Args:
        file_path: 文件路径

    Returns:
        是否有效
    """
    path = Path(file_path)
    return path.exists() and path.is_file()


def validate_api_key(api_key: Optional[str]) -> bool:
    """验证API密钥是否有效

    Args:
        api_key: API密钥

    Returns:
        是否有效
    """
    if not api_key:
        return False

    # 基本格式检查
    return len(api_key) > 10 and not api_key.isspace()