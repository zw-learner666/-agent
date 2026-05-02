from __future__ import annotations

import re
import time
from typing import Callable, Iterable, List, Optional

from .llm import LLMClient
from .models import Chapter, Character, ProjectState
from .style_library import render_style_prompt

LogCallback = Optional[Callable[[str], None]]


class NovelAgent:
    """Multi-step writing agent for long-form web novels."""

    def __init__(self, llm: Optional[LLMClient] = None) -> None:
        self.llm = llm or LLMClient(offline=True)

    def _emit(self, message: str, emit: LogCallback = None) -> None:
        line = f"[{time.strftime('%H:%M:%S')}] {message}"
        if emit:
            emit(line)

    def create_project(
        self,
        title: str,
        genre: str,
        premise: str,
        rules: str = "",
        tone: str = "热血、成长、悬念",
        style_key: str = "热血玄幻升级流",
        characters: Optional[List[Character]] = None,
        emit: LogCallback = None,
    ) -> ProjectState:
        self._emit("创建项目：写入世界观和初始人物。", emit)
        project = ProjectState.create(
            title=title,
            genre=genre,
            premise=premise,
            rules=rules,
            tone=tone,
            style_key=style_key,
            characters=characters or [],
        )
        self._emit("生成故事大纲：调用剧情规划 Agent。", emit)
        project.outline = self.generate_outline(project, emit=emit)
        project.memory["facts"].append(f"作品《{title}》的核心设定：{premise}")
        if rules:
            project.memory["facts"].append(f"世界规则：{rules}")
        project.memory["style_notes"].append(f"当前文风模板：{style_key}")
        project.touch()
        self._emit("项目创建完成。", emit)
        return project

    def generate_outline(self, project: ProjectState, emit: LogCallback = None) -> List[str]:
        style_prompt = render_style_prompt(project.style_key)
        user = f"""
请为这个网络小说项目生成一个三幕式故事大纲，每幕 3 个要点。要求每个要点都能服务于长篇连载。

{project.world.summary()}

人物：
{project.character_cards()}

{style_prompt}
""".strip()
        text = self.llm.generate(
            system="你是资深网文主编、剧情架构师和长篇连载顾问。",
            user=user,
            temperature=0.7,
            max_tokens=1400,
        )
        points = []
        for raw in re.split(r"\n+", text):
            clean = raw.strip(" -•\t")
            if clean:
                points.append(clean)
        if not points:
            points = [text.strip()]
        self._emit(f"大纲生成完成，共 {len(points)} 条。", emit)
        return points

    def add_character(self, project: ProjectState, character: Character, emit: LogCallback = None) -> ProjectState:
        project.characters.append(character)
        project.memory["facts"].append(
            f"人物 {character.name}：{character.role}；性格 {character.personality}；目标 {character.goal}。"
        )
        project.touch()
        self._emit(f"新增人物：{character.name}。", emit)
        return project

    def generate_chapter(
        self,
        project: ProjectState,
        chapter_goal: str,
        word_target: int = 1200,
        style_key: Optional[str] = None,
        custom_style_note: str = "",
        emit: LogCallback = None,
    ) -> Chapter:
        style_key = style_key or project.style_key
        steps = [
            "读取长期记忆与角色档案",
            "分析章节目标与读者期待",
            "人物行为模拟：检查每个角色的动机和压力",
            "剧情规划：设计冲突、爽点、转折和章末钩子",
            "文风适配：把抽象文风特征转为本项目原创语气",
            "生成章节正文",
            "一致性检查：世界观、人物、伏笔、节奏",
            "更新长期记忆",
        ]
        for step in steps[:5]:
            self._emit(step, emit)
            time.sleep(0.03)

        style_prompt = render_style_prompt(style_key, custom_style_note)
        plan_prompt = f"""
你是剧情规划 Agent。请先规划本章，不要写正文。
章节目标：{chapter_goal}
目标字数：{word_target}

世界观：
{project.world.summary()}

人物档案：
{project.character_cards()}

当前大纲：
{chr(10).join(project.outline[:12]) if project.outline else '暂无'}

长期记忆：
{project.memory_cards()}

请输出：
1. 本章标题候选 3 个
2. 本章冲突链
3. 关键人物行动
4. 需要新增或推进的伏笔
5. 章末钩子
""".strip()
        chapter_plan = self.llm.generate(
            system="你是网络小说剧情规划 Agent，擅长连载节奏、伏笔和人物驱动。",
            user=plan_prompt,
            temperature=0.65,
            max_tokens=1300,
        )
        self._emit("剧情规划完成。", emit)

        draft_prompt = f"""
你是章节写作 Agent。根据规划生成章节正文。

章节目标：{chapter_goal}
目标字数：约 {word_target} 字

剧情规划：
{chapter_plan}

项目设定：
{project.world.summary()}

人物档案：
{project.character_cards()}

长期记忆：
{project.memory_cards()}

{style_prompt}

写作要求：
- 章节必须有清晰事件推进，不要只写设定。
- 让人物像电子宠物一样有情绪反馈、关系变化或成长迹象。
- 章末保留一个钩子，驱动下一章。
- 不复制任何已有作品的原文或可识别表达。
- 输出章节正文，包含一个章节标题。
""".strip()
        self._emit("生成章节正文中。", emit)
        content = self.llm.generate(
            system="你是原创小说章节写作 Agent。",
            user=draft_prompt,
            temperature=0.85,
            max_tokens=max(1200, min(4000, word_target * 2)),
        )

        review_prompt = f"""
请对以下章节做一致性检查。输出：世界观、人物行为、伏笔、节奏、下一章建议。

项目记忆：
{project.memory_cards()}

章节目标：{chapter_goal}

章节正文：
{content[:6000]}
""".strip()
        self._emit("执行一致性检查。", emit)
        consistency_report = self.llm.generate(
            system="你是一致性检查 Agent，负责长篇小说设定、人物和伏笔维护。",
            user=review_prompt,
            temperature=0.4,
            max_tokens=1000,
        )

        title = self._extract_title(content, project.next_chapter_number())
        chapter = Chapter(
            number=project.next_chapter_number(),
            title=title,
            goal=chapter_goal,
            content=content,
            outline=chapter_plan,
            consistency_report=consistency_report,
            tokens_estimate=self.estimate_tokens(content + chapter_plan + consistency_report),
        )
        project.chapters.append(chapter)
        self._update_memory_after_chapter(project, chapter_goal, chapter, emit=emit)
        project.touch()
        self._emit(f"章节生成完成：第 {chapter.number} 章《{chapter.title}》。", emit)
        return chapter

    def _extract_title(self, content: str, number: int) -> str:
        for line in content.splitlines():
            clean = line.strip().strip("# ").strip()
            if not clean:
                continue
            clean = re.sub(r"^第?[一二三四五六七八九十百千万0-9]+[章节回幕卷、.：: -]*", "", clean).strip()
            if 2 <= len(clean) <= 30:
                return clean
        return f"第{number}章"

    def _update_memory_after_chapter(
        self,
        project: ProjectState,
        chapter_goal: str,
        chapter: Chapter,
        emit: LogCallback = None,
    ) -> None:
        project.memory["facts"].append(f"第 {chapter.number} 章已完成：{chapter_goal}")
        if "伏笔" in chapter.consistency_report:
            project.memory["open_threads"].append(
                f"第 {chapter.number} 章相关伏笔：围绕“{chapter_goal}”后续需要回收。"
            )
        if len(project.memory["facts"]) > 60:
            project.memory["facts"] = project.memory["facts"][-60:]
        if len(project.memory["open_threads"]) > 40:
            project.memory["open_threads"] = project.memory["open_threads"][-40:]
        self._emit("长期记忆已更新。", emit)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        # A rough mixed Chinese/English estimate; only used for UI planning.
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 0.8 + other_chars / 4)

    def summarize_project(self, project: ProjectState) -> str:
        return (
            f"《{project.title}》\n"
            f"类型：{project.world.genre}\n"
            f"文风：{project.style_key}\n"
            f"人物数：{len(project.characters)}\n"
            f"章节数：{len(project.chapters)}\n"
            f"记忆条目：{sum(len(v) for v in project.memory.values())}"
        )
