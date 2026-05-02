from __future__ import annotations

import argparse

from novel_agent.agent import NovelAgent
from novel_agent.commands import HELP_TEXT, run_command
from novel_agent.llm import LLMClient
from novel_agent.storage import load_project, save_project


def main() -> None:
    parser = argparse.ArgumentParser(description="Novel Agent Studio terminal")
    parser.add_argument("--project", help="Project id to load", default="")
    parser.add_argument("--offline", action="store_true", help="Use offline demo mode")
    parser.add_argument("--model", default=None, help="Model name")
    args = parser.parse_args()

    agent = NovelAgent(LLMClient(model=args.model, offline=args.offline))
    project = load_project(args.project) if args.project else None

    print("📖 Novel Agent Studio Terminal")
    print("输入 /help 查看命令；输入 /exit 退出。")
    if project:
        print(f"已加载项目：《{project.title}》 · {project.id}")

    def emit(line: str) -> None:
        print(line)

    while True:
        try:
            raw = input("novel-agent> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
        if raw in {"/exit", "exit", "quit"}:
            break
        if not raw:
            continue
        if raw == "/help":
            print(HELP_TEXT)
            continue
        result = run_command(raw, agent, project, emit=emit)
        project = result.project or project
        if project:
            save_project(project)
        print(result.message)
        if result.payload:
            print("\n--- 输出 ---")
            print(result.payload)
            print("--- 结束 ---\n")


if __name__ == "__main__":
    main()
