from api.db.models import Issue
from utils.markdownutil import MarkdownUtil


class GPTAnalyzer:
    def __init__(self):
        pass

    async def set_marks_by_body(self, i: Issue):
        assert isinstance(i, Issue)
        assert isinstance(i.body, str)

        text_body = MarkdownUtil().md_to_text(i.body)
        i.gpt_analysis = text_body
