from __future__ import annotations

import hashlib
import os
import random
import textwrap
from typing import Optional


def load_dotenv_if_exists(path: str = ".env") -> None:
    """Tiny .env loader to avoid adding another dependency."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


class LLMClient:
    """Small adapter for real LLM calls with a deterministic offline fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        offline: bool = False,
    ) -> None:
        load_dotenv_if_exists()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.offline = offline or not bool(self.api_key)

    def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.8,
        max_tokens: int = 1800,
    ) -> str:
        if self.offline:
            return self._offline_generate(system, user, max_tokens=max_tokens)

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover - depends on external service
            return (
                "[LLM 调用失败，已切换到离线演示文本]\n"
                f"错误：{exc}\n\n"
                + self._offline_generate(system, user, max_tokens=max_tokens)
            )

    def _offline_generate(self, system: str, user: str, max_tokens: int = 1800) -> str:
        seed_text = (system + "\n" + user)[:4000]
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)

        if "生成一个三幕式" in user or "故事大纲" in user:
            return textwrap.dedent(
                """
                第一幕：觉醒与绑定
                - 主角在日常危机中发现异常线索，与核心角色或神秘力量建立绑定。
                - 世界规则初次显露，主角获得一个看似微弱但可成长的能力。
                - 章末留下第一个长期伏笔：能力的来源并不属于当前时代。

                第二幕：试炼与关系变化
                - 主角进入更大的舞台，结识伙伴与竞争者。
                - 每个关键角色都有自己的目标、恐惧与隐藏代价。
                - 中段反转：主角以为在培养力量，实际上力量也在观察并塑造主角。

                第三幕：选择与第一次大事件
                - 敌对势力逼近，主角必须在保全自身与守护关系之间做选择。
                - 重要配角完成一次立场变化，关系网进入新阶段。
                - 第一卷结尾揭示世界观更深层危机，并打开下一卷地图。
                """
            ).strip()

        if "一致性检查" in user:
            return textwrap.dedent(
                """
                一致性检查报告：
                - 世界观：本章使用的能力、势力和地点未与已知设定冲突。
                - 人物：主角行为符合“谨慎但会在关键时刻承担风险”的成长方向。
                - 伏笔：新增“情绪会影响核心力量回应”的线索，建议后续三章内再次触发。
                - 风险：如果连续多章只给能力奖励，读者会降低紧张感，建议加入代价或误判。
                """
            ).strip()

        if "章节正文" in user or "生成正文" in user:
            names = ["林澈", "阿眠", "沈砚", "洛青岚"]
            hero = rng.choice(names)
            hook = rng.choice([
                "墙内传来第二次心跳",
                "烛火突然朝没有风的方向弯下去",
                "旧地图上多出了一条从未存在的河",
                "他掌心的印记像活物一样睁开了眼",
            ])
            title = rng.choice(["灰烬里的回声", "龙眠山的夜", "第一枚逆鳞", "风雪前的契约"])
            paragraphs = [
                f"### {title}",
                f"{hero}第一次意识到，自己养着的并不是一只温顺的宠物，而是一段正在苏醒的古老命运。",
                "傍晚的矿镇被细雨压得很低，屋檐下的水线像一排断续的琴弦。他把那枚温热的鳞片藏进袖口，听见它在皮肤上轻轻震动，仿佛某种幼小生灵隔着黑暗回应他的呼吸。",
                "白天发生的事仍在脑中回放：塌方、尖叫、被石粉遮住的天光，还有他伸手去拉那个孩子时，从掌心爆开的淡金色纹路。那一瞬间，所有碎石都停了半息。半息之后，世界重新坠落，而他已经不再是原来的自己。",
                f"夜里，{hook}。{hero}屏住呼吸，慢慢掀开木箱。箱底的黑布鼓起一个小小的弧度，像有什么东西正在里面蜷缩。",
                "“你听得懂我说话吗？”他低声问。",
                "黑布下没有声音。可他心底忽然浮起一种陌生的情绪：饥饿、戒备、委屈，以及一点点像火星般微弱的依赖。",
                "他愣住了。那不是语言，却比语言更直接。它把自己的害怕塞进他的胸口，也把他的犹豫照得无处可藏。",
                "门外传来脚步声。镇卫的铁靴踩过泥水，一下一下停在他的屋前。有人敲门，声音很客气，客气得像刀背贴着喉咙。",
                "“林家小子，开门。白天矿洞里的事，我们想问清楚。”",
                f"{hero}看着木箱。箱中的小东西也在看着他。那一刻，他突然明白，所谓培养从来不是单向的驯养。他给它名字、食物和藏身处；它给他勇气、危险，以及通向更大世界的第一把钥匙。",
                "他把鳞片按进掌心，疼痛像火线一样穿过血肉。下一刻，屋内所有影子同时向门口倾斜。",
                "“等一下。”他对门外说，声音比自己想象得平稳。",
                "木箱里传来细小的回应，像幼龙第一次磨动爪尖。",
                "这一夜之后，矿镇仍会下雨，山仍会沉默。但有些东西已经醒了。",
            ]
            return "\n\n".join(paragraphs)

        return textwrap.dedent(
            """
            离线演示结果：
            - 已解析用户设定。
            - 已生成一个可继续扩展的剧情节点。
            - 已维护人物目标、世界规则与伏笔列表。
            - 接入 API Key 后，此处会替换为真实模型输出。
            """
        ).strip()
