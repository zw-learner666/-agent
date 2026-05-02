import unittest

from novel_agent.agent import NovelAgent
from novel_agent.llm import LLMClient
from novel_agent.models import Character


class OfflineAgentTest(unittest.TestCase):
    def test_offline_agent_create_and_generate_chapter(self):
        agent = NovelAgent(LLMClient(offline=True))
        project = agent.create_project(
            title="测试作品",
            genre="东方玄幻",
            premise="主角绑定会成长的幼龙。",
            characters=[Character(name="林澈", role="主角", personality="谨慎", goal="保护幼龙")],
        )
        self.assertEqual(project.title, "测试作品")
        self.assertTrue(project.outline)

        chapter = agent.generate_chapter(project, "主角发现幼龙能回应情绪", word_target=800)
        self.assertEqual(chapter.number, 1)
        self.assertTrue(chapter.content)
        self.assertTrue(project.chapters)
        self.assertTrue(project.memory["facts"])


if __name__ == "__main__":
    unittest.main()
