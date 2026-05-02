from __future__ import annotations

import os
from pathlib import Path
from typing import List

import streamlit as st

from novel_agent.agent import NovelAgent
from novel_agent.commands import HELP_TEXT, run_command
from novel_agent.llm import LLMClient, load_dotenv_if_exists
from novel_agent.models import Character, ProjectState
from novel_agent.storage import export_markdown, list_projects, load_project, save_project, write_export
from novel_agent.style_library import STYLE_PRESETS, render_style_prompt, style_options

load_dotenv_if_exists()

st.set_page_config(
    page_title="Novel Agent Studio",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.block-container { padding-top: 1.5rem; }
.agent-card {
  border: 1px solid rgba(120, 120, 120, .18);
  border-radius: 18px;
  padding: 16px;
  background: rgba(250, 248, 240, .75);
  box-shadow: 0 6px 18px rgba(0,0,0,.04);
}
.terminal {
  background: #111827;
  color: #d1fae5;
  border-radius: 16px;
  padding: 16px;
  min-height: 260px;
  max-height: 420px;
  overflow-y: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 14px;
  line-height: 1.55;
  white-space: pre-wrap;
}
.flow {
  display: grid;
  grid-template-columns: repeat(5, minmax(110px, 1fr));
  gap: 10px;
  margin: 12px 0 18px;
}
.flow-box {
  border: 1px solid rgba(0,0,0,.12);
  border-radius: 14px;
  padding: 12px;
  background: #fffaf0;
  text-align: center;
  font-weight: 650;
}
.small-muted { color: #6b7280; font-size: 0.88rem; }
.metric-pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #f3f4f6;
  margin-right: 6px;
  margin-bottom: 6px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_state() -> None:
    st.session_state.setdefault("logs", [])
    st.session_state.setdefault("current_project_id", None)
    st.session_state.setdefault("last_payload", "")


def append_log(line: str) -> None:
    st.session_state.logs.append(line)
    if len(st.session_state.logs) > 200:
        st.session_state.logs = st.session_state.logs[-200:]


def get_agent() -> NovelAgent:
    api_key = st.session_state.get("api_key") or os.getenv("OPENAI_API_KEY", "")
    model = st.session_state.get("model") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    offline = st.session_state.get("offline", True)
    return NovelAgent(LLMClient(api_key=api_key, model=model, offline=offline))


def get_current_project() -> ProjectState | None:
    project_id = st.session_state.get("current_project_id")
    if not project_id:
        return None
    try:
        return load_project(project_id)
    except Exception:
        st.session_state.current_project_id = None
        return None


def set_current_project(project: ProjectState) -> None:
    st.session_state.current_project_id = project.id


def parse_characters(text: str) -> List[Character]:
    """Parse lines: name|role|personality|backstory|goal|secret."""
    characters: List[Character] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split("|")]
        while len(parts) < 6:
            parts.append("")
        characters.append(
            Character(
                name=parts[0] or "未命名角色",
                role=parts[1] or "配角",
                personality=parts[2],
                backstory=parts[3],
                goal=parts[4],
                secret=parts[5],
            )
        )
    return characters


def render_workflow_graph() -> None:
    st.markdown(
        """
<div class="flow">
  <div class="flow-box">用户输入<br><span class="small-muted">世界观 / 人物 / 文风</span></div>
  <div class="flow-box">剧情规划<br><span class="small-muted">冲突 / 伏笔 / 爽点</span></div>
  <div class="flow-box">人物模拟<br><span class="small-muted">性格 / 压力 / 成长</span></div>
  <div class="flow-box">章节生成<br><span class="small-muted">正文 / 对话 / 钩子</span></div>
  <div class="flow-box">记忆更新<br><span class="small-muted">事实 / 伏笔 / 反馈</span></div>
</div>
        """,
        unsafe_allow_html=True,
    )


init_state()

# Sidebar
with st.sidebar:
    st.title("📖 Novel Agent")
    st.caption("智能网络小说创作 Agent")

    st.session_state.offline = st.toggle(
        "离线演示模式",
        value=not bool(os.getenv("OPENAI_API_KEY")),
        help="无 API Key 时也能跑通工作流；接入真实模型后可关闭。",
    )
    st.session_state.api_key = st.text_input(
        "API Key（可选）",
        value="",
        type="password",
        help="仅保存在当前会话，不会写入文件。也可以放在 .env。",
    )
    st.session_state.model = st.text_input("模型名", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    st.divider()
    st.subheader("项目")
    projects = list_projects()
    project_labels = [f"{p.title} · {p.id}" for p in projects]
    if project_labels:
        selected = st.selectbox("选择已有项目", ["不选择"] + project_labels)
        if selected != "不选择":
            pid = selected.rsplit(" · ", 1)[-1]
            if st.session_state.current_project_id != pid:
                st.session_state.current_project_id = pid
                append_log(f"[UI] 已加载项目：{selected}")
                st.rerun()
    else:
        st.caption("暂无项目，请先创建。")

    if st.button("清空控制台日志"):
        st.session_state.logs = []
        st.rerun()

project = get_current_project()
agent = get_agent()

st.title("📚 智能网络小说 Agent Studio")
st.caption("图形化控制 + Web Terminal + 多 Agent 长篇写作工作流")
render_workflow_graph()

if project:
    st.markdown(
        f"<span class='metric-pill'>当前项目：{project.title}</span>"
        f"<span class='metric-pill'>人物：{len(project.characters)}</span>"
        f"<span class='metric-pill'>章节：{len(project.chapters)}</span>"
        f"<span class='metric-pill'>文风：{project.style_key}</span>",
        unsafe_allow_html=True,
    )
else:
    st.info("请在“创建项目”标签页新建项目，或用 Terminal 输入 `/new ...`。")

tab_create, tab_terminal, tab_project, tab_chapter, tab_memory, tab_export = st.tabs(
    ["创建项目", "控制台 Terminal", "项目设定", "生成章节", "记忆库", "导出"]
)

with tab_create:
    st.subheader("1. 创建一个新的小说 Agent 项目")
    col1, col2 = st.columns([1.1, 0.9])
    with col1:
        title = st.text_input("作品名", value="龙眠纪元")
        genre = st.text_input("类型", value="东方玄幻 / 电子宠物养成 / 冒险")
        premise = st.text_area(
            "核心设定",
            value="灵气枯竭的时代，矿镇少年意外绑定一只会随情绪进化的幼龙。主角像养电子宠物一样培养它，但幼龙也会反向影响主角性格与命运。",
            height=120,
        )
        rules = st.text_area(
            "世界规则",
            value="龙类早已灭绝；情绪、契约和记忆会影响灵兽进化；过度使用力量会留下精神代价。",
            height=100,
        )
        tone = st.text_input("整体基调", value="热血、成长、悬疑、陪伴感")
        style_key = st.selectbox("文风模板", style_options(), index=0)
    with col2:
        st.markdown("#### 初始人物")
        char_text = st.text_area(
            "每行一个人物：姓名|身份|性格|经历|目标|秘密",
            value=(
                "林澈|主角|谨慎、执着、有共情力|矿镇孤儿，靠修理旧机关为生|查清龙眠山真相|能听见幼龙的情绪\n"
                "阿眠|幼龙/电子宠物式伙伴|依赖、好奇、会吃醋|从古代龙茧中苏醒|学会理解人类并完成进化|记忆里藏着灭龙战争的真相\n"
                "沈砚|竞争者|冷静、骄傲、重规则|出身灵兽世家|证明契约术不是血统专利|家族正在追捕龙类遗物"
            ),
            height=230,
        )
        st.markdown("#### 文风说明")
        st.code(render_style_prompt(style_key), language="text")

    if st.button("🚀 创建项目并生成初始大纲", type="primary"):
        characters = parse_characters(char_text)
        new_project = agent.create_project(
            title=title,
            genre=genre,
            premise=premise,
            rules=rules,
            tone=tone,
            style_key=style_key,
            characters=characters,
            emit=append_log,
        )
        save_project(new_project)
        set_current_project(new_project)
        st.success(f"已创建项目：《{new_project.title}》")
        st.rerun()

with tab_terminal:
    st.subheader("2. Web Terminal：命令驱动 Agent")
    st.caption("可以把它当作小说 Agent 的控制台。")
    with st.expander("命令帮助", expanded=False):
        st.code(HELP_TEXT, language="text")

    command = st.text_input(
        "输入命令",
        value="/chapter goal=主角第一次发现幼龙会回应他的情绪 words=1200",
        key="terminal_command",
    )
    col_run, col_help = st.columns([1, 5])
    with col_run:
        run_btn = st.button("运行", type="primary")
    with col_help:
        st.caption("例如：/styles、/outline、/memory add=幼龙害怕雷声")

    if run_btn:
        result = run_command(command, agent, project, emit=append_log)
        if result.project:
            save_project(result.project)
            set_current_project(result.project)
            project = result.project
        st.session_state.last_payload = result.payload or result.message
        append_log(f"[Command] {command}")
        append_log(f"[Result] {result.message}")
        st.rerun()

    logs = "\n".join(st.session_state.logs[-120:]) or "等待命令输入..."
    st.markdown(f"<div class='terminal'>{logs}</div>", unsafe_allow_html=True)

    if st.session_state.last_payload:
        st.markdown("#### 最近输出")
        st.markdown(st.session_state.last_payload)

with tab_project:
    st.subheader("3. 项目设定与人物档案")
    if not project:
        st.warning("请先创建或选择项目。")
    else:
        col_world, col_chars = st.columns([1, 1])
        with col_world:
            st.markdown("#### 世界观")
            st.markdown(f"""
**作品名：** {project.world.title}  
**类型：** {project.world.genre}  
**核心设定：** {project.world.premise}  
**世界规则：** {project.world.rules or '待补充'}  
**整体基调：** {project.world.tone}  
**文风模板：** {project.style_key}
""")
            st.markdown("#### 大纲")
            if project.outline:
                for item in project.outline:
                    st.markdown(f"- {item}")
            else:
                st.caption("暂无大纲。")

        with col_chars:
            st.markdown("#### 人物")
            for c in project.characters:
                with st.container(border=True):
                    st.markdown(f"**{c.name}** · {c.role}")
                    st.write(f"性格：{c.personality or '未设定'}")
                    st.write(f"经历：{c.backstory or '未设定'}")
                    st.write(f"目标：{c.goal or '未设定'}")
                    st.write("状态：" + " / ".join(f"{k} {v}" for k, v in c.stats.items()))

            with st.expander("新增人物"):
                name = st.text_input("姓名", key="new_char_name")
                role = st.text_input("身份", value="配角", key="new_char_role")
                personality = st.text_input("性格", key="new_char_personality")
                backstory = st.text_area("经历", key="new_char_backstory")
                goal = st.text_input("目标", key="new_char_goal")
                secret = st.text_input("秘密", key="new_char_secret")
                if st.button("添加人物"):
                    if name.strip():
                        agent.add_character(
                            project,
                            Character(name, role, personality, backstory, goal, secret),
                            emit=append_log,
                        )
                        save_project(project)
                        st.success(f"已添加人物：{name}")
                        st.rerun()
                    else:
                        st.error("人物姓名不能为空。")

with tab_chapter:
    st.subheader("4. 生成章节")
    if not project:
        st.warning("请先创建或选择项目。")
    else:
        col_a, col_b = st.columns([1, 1])
        with col_a:
            chapter_goal = st.text_area(
                "本章目标",
                value="主角第一次发现幼龙会回应他的情绪；镇卫上门盘问；主角决定保护幼龙。",
                height=120,
            )
            word_target = st.slider("目标字数", 600, 5000, 1200, step=100)
            chapter_style = st.selectbox("本章文风", style_options(), index=style_options().index(project.style_key) if project.style_key in style_options() else 0)
            custom_style_note = st.text_area("额外文风备注（可选）", value="让幼龙像电子宠物一样有明确情绪反馈，但保持玄幻主线张力。", height=80)
            generate_btn = st.button("✍️ 运行多 Agent 工作流生成章节", type="primary")
        with col_b:
            st.markdown("#### 当前记忆摘要")
            st.markdown(project.memory_cards())

        if generate_btn:
            with st.spinner("Agent 正在规划、模拟、写作和检查..."):
                chapter = agent.generate_chapter(
                    project,
                    chapter_goal=chapter_goal,
                    word_target=word_target,
                    style_key=chapter_style,
                    custom_style_note=custom_style_note,
                    emit=append_log,
                )
                save_project(project)
                st.session_state.last_payload = chapter.content
            st.success(f"已生成第 {chapter.number} 章：《{chapter.title}》")
            st.rerun()

        if project.chapters:
            latest = project.chapters[-1]
            st.markdown(f"### 最近章节：第 {latest.number} 章《{latest.title}》")
            st.markdown(latest.content)
            with st.expander("查看剧情规划与一致性检查"):
                st.markdown("#### 剧情规划")
                st.markdown(latest.outline)
                st.markdown("#### 一致性检查")
                st.markdown(latest.consistency_report)

with tab_memory:
    st.subheader("5. 长期记忆库")
    if not project:
        st.warning("请先创建或选择项目。")
    else:
        st.markdown(project.memory_cards())
        with st.expander("写入新记忆 / 反馈"):
            memory_item = st.text_input("事实或伏笔")
            feedback_item = st.text_input("读者/用户反馈")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                if st.button("写入事实记忆") and memory_item.strip():
                    project.memory.setdefault("facts", []).append(memory_item.strip())
                    save_project(project)
                    st.success("已写入事实记忆。")
                    st.rerun()
            with col_m2:
                if st.button("写入反馈") and feedback_item.strip():
                    project.memory.setdefault("reader_feedback", []).append(feedback_item.strip())
                    save_project(project)
                    st.success("已写入反馈。")
                    st.rerun()

with tab_export:
    st.subheader("6. 导出项目")
    if not project:
        st.warning("请先创建或选择项目。")
    else:
        md = export_markdown(project)
        st.download_button(
            "下载 Markdown",
            data=md.encode("utf-8"),
            file_name=f"{project.title}_{project.id}.md",
            mime="text/markdown",
        )
        if st.button("写入 workspace/exports 文件夹"):
            path = write_export(project)
            st.success(f"已导出：{path}")
        st.markdown("#### 预览")
        st.code(md[:6000] + ("\n..." if len(md) > 6000 else ""), language="markdown")

st.divider()
st.caption("Novel Agent Studio · 本地优先 · 长篇记忆 · 原创文风特征卡")
