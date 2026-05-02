from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from .models import ProjectState, utc_now


def workspace_dir() -> Path:
    return Path(os.getenv("NOVEL_AGENT_WORKSPACE", "workspace"))


def projects_dir() -> Path:
    path = workspace_dir() / "projects"
    path.mkdir(parents=True, exist_ok=True)
    return path


def exports_dir() -> Path:
    path = workspace_dir() / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def project_path(project_id: str) -> Path:
    return projects_dir() / f"{project_id}.json"


def save_project(project: ProjectState) -> Path:
    project.touch()
    path = project_path(project.id)
    with path.open("w", encoding="utf-8") as f:
        json.dump(project.to_dict(), f, ensure_ascii=False, indent=2)
    return path


def load_project(project_id: str) -> ProjectState:
    path = project_path(project_id)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return ProjectState.from_dict(data)


def list_projects() -> List[ProjectState]:
    items: List[ProjectState] = []
    for path in sorted(projects_dir().glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            with path.open("r", encoding="utf-8") as f:
                items.append(ProjectState.from_dict(json.load(f)))
        except Exception:
            continue
    return items


def find_project_by_title(title: str) -> Optional[ProjectState]:
    for project in list_projects():
        if project.title == title:
            return project
    return None


def export_markdown(project: ProjectState) -> str:
    lines = [
        f"# {project.title}",
        "",
        f"导出时间：{utc_now()}",
        "",
        "## 世界观设定",
        "",
        project.world.summary(),
        "",
        f"文风模板：{project.style_key}",
        "",
        "## 人物档案",
        "",
        project.character_cards(),
        "",
        "## 故事大纲",
        "",
    ]
    if project.outline:
        lines.extend(f"{i + 1}. {item}" for i, item in enumerate(project.outline))
    else:
        lines.append("暂无大纲。")

    lines.extend(["", "## 长期记忆", "", project.memory_cards(), "", "## 章节正文", ""])
    if project.chapters:
        for chapter in project.chapters:
            lines.extend([
                f"### 第 {chapter.number} 章：{chapter.title}",
                "",
                f"章节目标：{chapter.goal}",
                "",
                chapter.content,
                "",
                "#### 一致性检查",
                "",
                chapter.consistency_report or "暂无。",
                "",
            ])
    else:
        lines.append("暂无章节。")
    return "\n".join(lines)


def write_export(project: ProjectState) -> Path:
    filename = f"{project.title}_{project.id}.md".replace("/", "_")
    path = exports_dir() / filename
    path.write_text(export_markdown(project), encoding="utf-8")
    return path
