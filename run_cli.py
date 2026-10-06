import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.prompt import Prompt
from orchestrator import PCAgentOrchestrator

console = Console()

def main():
    orchestrator = PCAgentOrchestrator()
    console.print("[bold green]══════════════════════════════════════════════════════════════════════[/bold green]")
    console.print("[bold yellow] 🤖 PC-AGENTINTEL: HỆ THỐNG MULTI-AGENT TƯ VẤN & KIỂM ĐỊNH PHẦN CỨNG [/bold yellow]")
    console.print("[bold green]══════════════════════════════════════════════════════════════════════[/bold green]\n")

    while True:
        query = Prompt.ask("[bold yellow]Nhập yêu cầu của bạn (hoặc gõ 'exit' để thoát)[/bold yellow]")

        if not query.strip():
            continue

        if query.strip().lower() in ["exit", "quit", "0", "thoat", "thoát"]:
            console.print("[bold red]Đã thoát chương trình. Tạm biệt![/bold red]")
            break

        print("\n")
        orchestrator.run(query.strip(), show_steps=False)
        console.print("\n" + "─" * 70 + "\n")

if __name__ == "__main__":
    main()
