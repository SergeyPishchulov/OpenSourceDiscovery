from api.db.models import Issue
from gpt_api.gpt_client import GPTClient
from utils.markdownutil import MarkdownUtil


class GPTAnalyzer:
    def __init__(self):
        self.gpt_client = GPTClient()

    async def set_marks_by_body(self, i: Issue):
        assert isinstance(i, Issue)
        assert isinstance(i.body, str)

        text_body = MarkdownUtil().md_to_text(i.body)
        i.gpt_analysis = await self.get_size(title=i.title,
                                             body=text_body)

    async def get_size(self, title, body):
        return await self.gpt_client.send(content=self.get_prompt(title, body))

    def get_prompt(self, title, body):
        prompt =  ("I will show you an issue from GitHub."
                "This is a text of the issue:"
                f"{title}. {body}"
                f"Is this issue a small, medium or big task?")
        print(prompt)
        return prompt
