from langchain_core.tools import tool
import asyncio
from rich.console import Console
from rich.prompt import Prompt

console = Console()


@tool
async def ask_user(question: str) -> str:
    """异步向用户询问问题并获取回答

    Args:
        question: 要询问的问题

    Returns:
        用户的回答（y/n/其他输入）
    """
    # 在异步环境中获取用户输入
    loop = asyncio.get_event_loop()

    try:
        # 使用 Rich Prompt 美化输出
        console.print(f"\n[cyan bold]❓ {question}[/cyan bold]")
        
        # 使用 run_in_executor 避免阻塞事件循环
        response = await loop.run_in_executor(
            None,
            lambda: Prompt.ask(
                "[yellow]请输入[/yellow]",
                choices=["y", "n", "yes", "no", "是", "否"],
                default="y"
            )
        )
        return response.strip().lower()
    except KeyboardInterrupt:
        return "n"
    except Exception as e:
        console.print(f"[red]输入错误：{e}[/red]")
        return "n"