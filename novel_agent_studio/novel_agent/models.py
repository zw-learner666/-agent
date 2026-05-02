from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Character:
    name: str
    role: str = "配角"
    personality: str = ""
    backstory: str = ""
    goal: str = ""
    secret: str = ""
    growth_stage: str = "初始"
    relationships: Dict[str, str] = field(default_factory=dict)
    stats: Dict[str, int] = field(default_factory=lambda: {
        "好感度": 50,
        "压力值": 20,
        "行动力": 60,
        "黑化风险": 10,
    })

    def short_card(self) -> str:
        return (
            f"- {self.name}（{self.role}）：性格={self.personality or '未设定'}；"
            f"经历={self.backstory or '未设定'}；目标={self.goal or '未设定'}；"
            f"成长阶段={self.growth_stage}"
        )


@dataclass
class WorldSetting:
    title: str
    genre: str = "网络小说"
    premise: str = ""
    rules: str = ""
    tone: str = "热血、成长、悬念"
    audience: str = "喜欢长篇连载与角色养成的读者"
    forbidden: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"作品名：{self.title}\n"
            f"类型：{self.genre}\n"
            f"核心设定：{self.premise}\n"
            f"世界规则：{self.rules or '待补充'}\n"
            f"整体基调：{self.tone}\n"
            f"目标读者：{self.audience}"
        )


@dataclass
class Chapter:
    number: int
    title: str
    goal: str
    content: str
    outline: str = ""
    consistency_report: str = ""
    created_at: str = field(default_factory=utc_now)
    tokens_estimate: int = 0


@dataclass
class ProjectState:
    id: str
    title: str
    world: WorldSetting
    style_key: str = "热血玄幻升级流"
    characters: List[Character] = field(default_factory=list)
    outline: List[str] = field(default_factory=list)
    chapters: List[Chapter] = field(default_factory=list)
    memory: Dict[str, List[str]] = field(default_factory=lambda: {
        "facts": [],
        "open_threads": [],
        "resolved_threads": [],
        "reader_feedback": [],
        "style_notes": [],
    })
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        title: str,
        genre: str,
        premise: str,
        rules: str = "",
        tone: str = "热血、成长、悬念",
        style_key: str = "热血玄幻升级流",
        characters: Optional[List[Character]] = None,
    ) -> "ProjectState":
        world = WorldSetting(title=title, genre=genre, premise=premise, rules=rules, tone=tone)
        return cls(
            id=str(uuid4())[:8],
            title=title,
            world=world,
            style_key=style_key,
            characters=characters or [],
        )

    def touch(self) -> None:
        self.updated_at = utc_now()

    def next_chapter_number(self) -> int:
        return len(self.chapters) + 1

    def character_cards(self) -> str:
        if not self.characters:
            return "暂无人物。"
        return "\n".join(c.short_card() for c in self.characters)

    def memory_cards(self) -> str:
        sections = []
        for key, label in [
            ("facts", "已确定事实"),
            ("open_threads", "未回收伏笔"),
            ("resolved_threads", "已回收伏笔"),
            ("reader_feedback", "读者/用户反馈"),
            ("style_notes", "文风注意事项"),
        ]:
            items = self.memory.get(key, [])
            body = "\n".join(f"- {item}" for item in items) if items else "- 暂无"
            sections.append(f"### {label}\n{body}")
        return "\n\n".join(sections)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectState":
        world_data = data.get("world", {})
        world = WorldSetting(**world_data)

        characters = [Character(**item) for item in data.get("characters", [])]
        chapters = [Chapter(**item) for item in data.get("chapters", [])]

        default_memory = {
            "facts": [],
            "open_threads": [],
            "resolved_threads": [],
            "reader_feedback": [],
            "style_notes": [],
        }
        default_memory.update(data.get("memory", {}) or {})

        return cls(
            id=data["id"],
            title=data.get("title", world.title),
            world=world,
            style_key=data.get("style_key", "热血玄幻升级流"),
            characters=characters,
            outline=data.get("outline", []),
            chapters=chapters,
            memory=default_memory,
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )
