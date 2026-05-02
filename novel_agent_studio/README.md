# Novel Agent Studio：智能网络小说创作 Agent

一个可直接上传 GitHub 的本地 Web 应用，用于搭建“智能网络小说创作 Agent”。它支持：

- 图形化 Web 控制台：世界观、人物、文风、章节目标可视化编辑。
- Web Terminal：用命令驱动 Agent 工作流，例如 `/chapter goal=主角第一次觉醒 words=1200`。
- 多 Agent 协作：剧情规划、人物模拟、文风适配、一致性检查、长期记忆维护。
- 长篇记忆库：记录角色关系、已发生事件、伏笔、用户反馈，降低设定冲突。
- 离线演示模式：没有 API Key 也能跑通流程，方便展示和二次开发。
- Markdown 导出：把项目设定、人物、章节、记忆导出为文档。

> 合规说明：本项目内置的是“文风特征卡”，用于抽象描述叙事节奏、句式密度、氛围与视角等写作特征；不鼓励复制任何作者的原文、段落、固定句式或在世作者的精准仿写。

---

## 1. 快速开始

```bash
# 1) 克隆或解压项目
cd novel_agent_studio

# 2) 建议使用虚拟环境
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3) 安装依赖
pip install -r requirements.txt

# 4) 可选：配置真实 LLM
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY

# 5) 启动 Web 图形化控制台
streamlit run app.py
```

启动后浏览器会打开本地页面，默认地址通常是：

```text
http://localhost:8501
```

没有 API Key 时，勾选“离线演示模式”，也可以完整体验工作流。

---

## 2. 项目结构

```text
novel_agent_studio/
├── app.py                         # Streamlit Web 图形化控制台
├── terminal_agent.py              # 命令行入口
├── requirements.txt               # Python 依赖
├── .env.example                   # 环境变量示例
├── .gitignore
├── novel_agent/
│   ├── __init__.py
│   ├── agent.py                   # 核心 Agent 工作流
│   ├── commands.py                # Web Terminal 命令解析
│   ├── llm.py                     # LLM 适配器 + 离线 mock
│   ├── models.py                  # 数据结构
│   ├── storage.py                 # 本地 JSON 存储与导出
│   └── style_library.py           # 文风特征卡
└── tests/
    └── test_offline_agent.py      # 离线单元测试
```

---

## 3. Web Terminal 命令

在 Web 页面“控制台 Terminal”里可以输入：

```text
/help
```

查看命令帮助。

常用示例：

```text
/new title=龙眠纪元 genre=东方玄幻 premise=主角在灵气枯竭时代养成一条会进化的龙
```

```text
/char name=林澈 role=主角 personality=谨慎、执着、有共情力 backstory=矿镇孤儿 goal=查清龙眠山真相
```

```text
/outline
```

```text
/chapter goal=主角第一次发现龙蛋会回应他的情绪 words=1200 style=热血玄幻升级流
```

```text
/export
```

---

## 4. 命令行运行

```bash
python terminal_agent.py --offline
```

启动后可在终端输入和 Web Terminal 相同的命令。

---

## 5. 配置真实模型

复制 `.env.example` 为 `.env`：

```bash
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-4o-mini
NOVEL_AGENT_WORKSPACE=workspace
```

或者在 Web 页面左侧栏直接输入 API Key。

---

## 6. 上传到 GitHub

```bash
cd novel_agent_studio
git init
git add .
git commit -m "init novel agent studio"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

---

## 7. 可继续扩展的方向

- 接入向量数据库：把长篇记忆、角色档案、章节内容做 RAG 检索。
- 增加多模型路由：剧情规划用强推理模型，正文润色用高性价比模型。
- 接入用户反馈评分：根据读者偏好自动调整节奏和冲突强度。
- 增加“人物电子宠物”面板：显示好感度、压力值、目标变化、关系图。
- 支持章节批量生成与连载排期。

---

## License

MIT
