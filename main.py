#!/usr/bin/env python3
"""智能运维故障排查助手 - 主程序入口

使用方法:
    python main.py diagnose <log_file>              # 诊断指定日志文件
    python main.py diagnose <log_file> --path       # 指定绝对路径
    python main.py chat                             # 启动对话模式

示例:
    python main.py diagnose sample_error.log
    python main.py diagnose /var/log/application.log
    python main.py chat
"""

import sys
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.agent.diagnosis_agent import DiagnosisAgent
from config.settings import settings
from src.utils.logger import setup_logger

# 初始化Rich控制台
console = Console()


def setup():
    """初始化设置

    Returns:
        配置好的日志记录器
    """
    # 设置日志
    logger = setup_logger(
        name="ops_agent",
        level=settings.log_level,
        log_file=settings.log_file,
    )

    # 检查API密钥
    if not settings.glm_api_key:
        console.print("[red]错误: 请在 .env 文件中设置 API_KEY[/red]")
        sys.exit(1)

    return logger


def show_welcome():
    """显示欢迎信息"""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]智能运维故障排查助手[/bold cyan]\n"
        "[dim]基于LangChain Agent的智能诊断系统[/dim]\n"
        "[dim]支持异步处理和指定日志路径[/dim]",
        border_style="cyan",
    ))
    console.print()


async def diagnose_command_async(args):
    """异步执行诊断命令

    Args:
        args: 命令行参数
    """
    logger = setup()
    show_welcome()

    # 解析日志文件路径
    log_file = Path(args.log_file)

    # 如果指定了绝对路径或路径不存在于当前目录
    if not log_file.exists():
        # 尝试作为绝对路径
        if not log_file.is_absolute():
            console.print(f"[red]错误: 日志文件不存在: {log_file}[/red]")
            console.print("[dim]提示: 请检查文件路径是否正确[/dim]")
            sys.exit(1)

    # 显示诊断信息
    console.print(f"[yellow]📁 日志文件:[/yellow] {log_file.absolute()}")
    console.print(f"[yellow]🤖 使用模型:[/yellow] {settings.llm_model}")
    console.print(f"[yellow]🌡️  温度:[/yellow] {settings.llm_temperature}")
    console.print(f"[yellow]⚡ 异步模式:[/yellow] 已启用")
    console.print()

    # 创建诊断智能体
    console.print("[cyan]正在初始化智能体（首次调用可能较慢）...[/cyan]")
    max_errors = args.max_errors if args.max_errors else settings.max_error_lines
    parallel = args.parallel if args.parallel else settings.parallel_analysis
    agent = DiagnosisAgent(max_error_lines=max_errors, parallel_analysis=parallel)
    console.print(f"[dim]最大读取 ERROR 日志数量: {max_errors}, 并行模式: {parallel}[/dim]")

    # 执行诊断
    try:
        console.print("[cyan]开始诊断...[/cyan]")
        console.print("[dim]" + "─" * 60 + "[/dim]")
        console.print()

        # 异步调用
        result = await agent.diagnose_with_path(str(log_file.absolute()))

        console.print()
        console.print("[dim]" + "─" * 60 + "[/dim]")
        console.print()
        console.print(Panel.fit(
            "[bold green]✅ 诊断完成！[/bold green]\n\n"
            f"[cyan]📄 报告已生成: output/diagnosis_report.md[/cyan]",
            border_style="green",
        ))

    except FileNotFoundError as e:
        console.print(f"\n[red]❌ 文件错误: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  用户中断诊断[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"诊断失败: {e}", exc_info=True)
        console.print(f"\n[red]❌ 诊断失败: {e}[/red]")
        sys.exit(1)


def diagnose_command(args):
    """诊断命令入口（同步包装）"""
    asyncio.run(diagnose_command_async(args))


async def chat_command_async(args):
    """异步对话模式

    Args:
        args: 命令行参数
    """
    setup()
    show_welcome()

    console.print("[cyan]🤖 智能运维故障排查助手 - 对话模式[/cyan]")
    console.print("[dim]输入 'quit' 或 'exit' 退出[/dim]")
    console.print("[dim]输入日志路径开始诊断，例如: /var/log/app.log[/dim]")
    console.print("[dim]" + "─" * 60 + "[/dim]")

    agent = DiagnosisAgent()

    while True:
        try:
            console.print()
            user_input = console.input("[bold cyan]你:[/bold cyan] ").strip()

            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                console.print("\n[yellow]再见！👋[/yellow]")
                break

            if not user_input:
                continue

            # 检查是否是日志路径
            if Path(user_input).exists() and Path(user_input).is_file():
                console.print(f"\n[cyan]检测到日志文件，开始诊断...[/cyan]")
                result = await agent.diagnose_with_path(user_input)
                console.print(f"\n[bold green]助手:[/bold green] {result}")
            else:
                # 普通对话
                console.print()
                with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                ) as progress:
                    progress.add_task("思考中...", total=None)
                    response = await agent.chat(user_input)

                console.print(f"[bold green]助手:[/bold green] {response}")

        except KeyboardInterrupt:
            console.print("\n[yellow]再见！👋[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]❌ 错误: {e}[/red]")


def chat_command(args):
    """对话命令入口（同步包装）"""
    asyncio.run(chat_command_async(args))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能运维故障排查助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py diagnose sample_error.log
  python main.py diagnose /var/log/application.log
  python main.py chat
        """,
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # diagnose 子命令
    diagnose_parser = subparsers.add_parser(
        'diagnose',
        help='诊断日志文件',
        description='诊断指定路径的日志文件，支持绝对路径和相对路径'
    )
    diagnose_parser.add_argument(
        'log_file',
        help='要诊断的日志文件路径（支持绝对路径和相对路径）'
    )
    diagnose_parser.add_argument(
        '--max-errors', '-m',
        type=int,
        default=None,
        help='最大读取的ERROR日志数量（默认从.env读取）'
    )
    diagnose_parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='启用并行分析模式（更快，但无交互）'
    )

    # chat 子命令
    chat_parser = subparsers.add_parser(
        'chat',
        help='启动对话模式',
        description='启动交互式对话模式，可以直接输入日志路径进行诊断'
    )

    args = parser.parse_args()

    if args.command == 'diagnose':
        diagnose_command(args)
    elif args.command == 'chat':
        chat_command(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()