"""对话记忆管理（预留扩展）"""
from typing import List, Dict, Any
from datetime import datetime


class ConversationMemory:
    """对话记忆管理器

    用于存储和管理对话历史（预留扩展）
    """

    def __init__(self, max_history: int = 100):
        """初始化记忆管理器

        Args:
            max_history: 最大历史记录数
        """
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str) -> None:
        """添加消息到历史记录

        Args:
            role: 角色
            content: 消息内容
        """
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

        # 限制历史记录数量
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self) -> List[Dict[str, Any]]:
        """获取对话历史

        Returns:
            对话历史列表
        """
        return self.history

    def clear(self) -> None:
        """清空对话历史"""
        self.history = []