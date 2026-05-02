from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .agent import NovelAgent
from .models import Character, ProjectState
from .storage import save_project, write_export
from .style_library import style_options


HELP_TEXT = """
可用命令：
/help
/new title=作品名 genre=类型 premise=核心设定 [rules=世界规则] [tone=基调]
/char name=姓名 role=身份 personality=性格 backstory=经历 goal=目标 [secret=秘密]
/outline
/chapter goal=本章目标 [words=1200] [style=热血玄幻升级流]
/memory add=需要写入长期记忆的一句话
/feedback text=读者或作者反馈
/export
/styles
""".strip()


@dataclass
class CommandResult:
    message: str
    project: Optional[ProjectState] = None
    payload: Optional[str] = None


def parse_kv(command: str) -> Tuple[str, Dict[str, str]]:
    parts = shlex.split(command)
    if not parts:
        return "", {}
    name = parts[0]
    args: Dict[str, str] = {}
    loose = []
    for item in parts[1:]:
        if "=" in item:
            k, v = item.split("=", 1)
            args[k.strip()] = v.strip()
        else:
            loose.append(item)
    if loose:
        args["text"] = " ".join(loose)
    return name, args


def run_command(
    raw: str,
    agent: NovelAgent,
    project: Optional[ProjectState],
    emit=None,
) -> CommandResult:
    raw = raw.strip()
    if not raw:
        return CommandResult("请输入命令。", project)
    name, args = parse_kv(raw)

    if name == "/help":
        return CommandResult(HELP_TEXT, project)

    if name == "/styles":
        return CommandResult("可选文风：\n" + "\n".join(f"- {s}" for s in style_options()), project)

    if name == "/new":
        title = args.get("title", "未命名项目")
        genre = args.get("genre", "网络小说")
        premise = args.get("premise", args.get("text", "主角与一个会成长的神秘伙伴共同冒险。"))
        rules = args.get("rules", "")
        tone = args.get("tone", "热血、成长、悬念")
        style = args.get("style", "热血玄幻升级流")
        new_project = agent.create_project(title, genre, premise, rules, tone, style, emit=emit)
        save_project(new_project)
        return CommandResult(f"已创建项目：《{title}》。", new_project)

    if project is None:
        return CommandResult("请先用 /new 创建项目，或在侧栏选择已有项目。", project)

    if name == "/char":
        char = Character(
            name=args.get("name", "未命名角色"),
            role=args.get("role", "配角"),
            personality=args.get("personality", ""),
            backstory=args.get("backstory", ""),
            goal=args.get("goal", ""),
            secret=args.get("secret", ""),
        )
        agent.add_character(project, char, emit=emit)
        save_project(project)
        return CommandResult(f"已添加人物：{char.name}。", project)

    if name == "/outline":
        project.outline = agent.generate_outline(project, emit=emit)
        save_project(project)
        return CommandResult("大纲已重新生成。", project, payload="\n".join(project.outline))

    if name == "/chapter":
        goal = args.get("goal", args.get("text", "推进主线，并让主角获得一次成长反馈"))
        words = int(args.get("words", "1200"))
        style = args.get("style", project.style_key)
        chapter = agent.generate_chapter(project, goal, word_target=words, style_key=style, emit=emit)
        save_project(project)
        return CommandResult(f"已生成第 {chapter.number} 章：《{chapter.title}》。", project, payload=chapter.content)

    if name == "/memory":
        item = args.get("add", args.get("text", ""))
        if not item:
            return CommandResult("请使用 /memory add=记忆内容。", project)
        project.memory.setdefault("facts", []).append(item)
        save_project(project)
        return CommandResult("已写入长期记忆。", project)

    if name == "/feedback":
        text = args.get("text", args.get("add", ""))
        if not text:
            return CommandResult("请使用 /feedback text=反馈内容。", project)
        project.memory.setdefault("reader_feedback", []).append(text)
        save_project(project)
        return CommandResult("已记录反馈。", project)

    if name == "/export":
        path = write_export(project)
        return CommandResult(f"已导出 Markdown：{path}", project, payload=str(path))

    return CommandResult(f"未知命令：{name}\n\n{HELP_TEXT}", project)
