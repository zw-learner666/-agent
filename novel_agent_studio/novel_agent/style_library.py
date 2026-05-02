from __future__ import annotations

from typing import Dict


STYLE_PRESETS: Dict[str, Dict[str, str]] = {
    "热血玄幻升级流": {
        "label": "热血玄幻升级流",
        "description": "宏大世界观、强冲突、升级反馈明确、章末留钩子。",
        "voice": "句子有力量感，战斗与成长节点清晰，情绪推进强。",
        "rhythm": "快节奏；每章至少有一个明确爽点或悬念。",
        "avoid": "避免堆砌空泛形容词；避免复制任何具体作者的固定表达。",
    },
    "学院成长冒险流": {
        "label": "学院成长冒险流",
        "description": "伙伴组队、阶段任务、轻松热血、情感关系逐步升温。",
        "voice": "语言明快，重视友情、竞争和阶段性成长。",
        "rhythm": "中快节奏；用训练、试炼、比赛、危机推动升级。",
        "avoid": "避免人物过度工具化；避免套路奖励没有代价。",
    },
    "细腻权谋群像流": {
        "label": "细腻权谋群像流",
        "description": "多人物视角、对话含潜台词、权力博弈、伏笔密集。",
        "voice": "克制、精确、重视人物心理与话外之意。",
        "rhythm": "中速；以信息差、选择代价和关系变化制造张力。",
        "avoid": "避免把阴谋解释得太直白；避免所有角色都同一种口吻。",
    },
    "现代内省文学感": {
        "label": "现代内省文学感",
        "description": "孤独感、都市疏离、隐喻意象、人物内在矛盾。",
        "voice": "冷静、细腻、留白，重视感官细节与情绪余味。",
        "rhythm": "慢到中速；让外部事件映照人物精神变化。",
        "avoid": "避免精准模仿在世作家；避免大量无事件的自我沉溺。",
    },
    "十九世纪现实主义长篇": {
        "label": "十九世纪现实主义长篇",
        "description": "社会结构、家族关系、道德抉择、宏观时代背景。",
        "voice": "沉稳、细致，兼顾社会观察和人物命运。",
        "rhythm": "中慢速；用关系、阶层、历史压力推动剧情。",
        "avoid": "避免直接挪用公共领域作品段落；避免现代网络梗破坏语感。",
    },
    "史诗浪漫冒险": {
        "label": "史诗浪漫冒险",
        "description": "强命运感、宏大场景、牺牲与理想、浪漫主义情绪。",
        "voice": "富有画面感，善用象征、誓言、群体场面。",
        "rhythm": "中快节奏；大事件与人物情感同时推进。",
        "avoid": "避免过度咏叹；避免角色动机只靠口号。",
    },
    "轻喜剧互动日常": {
        "label": "轻喜剧互动日常",
        "description": "电子宠物式陪伴、日常任务、吐槽、温暖关系成长。",
        "voice": "轻松、有梗、亲切，允许适量弹幕式互动。",
        "rhythm": "快节奏短回合；每段都有小反馈、小变化。",
        "avoid": "避免只有玩梗没有剧情；避免角色成长停滞。",
    },
}


STYLE_POLICY = """
文风安全边界：
1. 可以学习“抽象写作特征”：节奏、视角、氛围、冲突密度、对白功能、篇章结构。
2. 不复制任何作者的原文、段落、固定句式、独特比喻链或可识别表达。
3. 对在世作者，只能使用宽泛风格描述，不生成“精准仿写”。
4. 输出应形成用户项目自己的原创声音。
""".strip()


def get_style_card(style_key: str) -> Dict[str, str]:
    return STYLE_PRESETS.get(style_key, STYLE_PRESETS["热血玄幻升级流"])


def style_options() -> list[str]:
    return list(STYLE_PRESETS.keys())


def render_style_prompt(style_key: str, custom_style_note: str = "") -> str:
    card = get_style_card(style_key)
    custom = f"\n用户额外文风要求：{custom_style_note}" if custom_style_note else ""
    return f"""
文风特征卡：{card['label']}
描述：{card['description']}
语言声音：{card['voice']}
节奏要求：{card['rhythm']}
避免事项：{card['avoid']}
{STYLE_POLICY}{custom}
""".strip()
