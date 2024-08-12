from markdown import Markdown, markdown
from io import StringIO
from bs4 import BeautifulSoup

# s = "# Description\r\nI'm using siglens version 0.2.24. If you enter a query in query mode \"code\" (at least for query language \"Splunk QL\") as soon as you enter a pipe character (\"|\") a newline gets inserted. Gives a nice query but is not very user friendly (if you are writing the query you do not expect that suddenly a new line gets created even you didn't hit \"enter\".\r\n\r\nAdditional if the query spans multiple lines as soon as you hit the search button (or elsewhere outside of the search bar) it gets collapsed back to one line. Together with the upper \"behaviour\" you only see the first part of you query - the rest is hidden.\r\n\r\nIn my opinion the search bar should stay extended and should show as many lines as your query has.\r\n\r\n# Steps to Reproduce\r\nGive detailed step-by-step instructions to help us easily reproduce the issue.\r\n1. go to Logs, switch to query mode \"code\" and query language \"Splunk QL\"\r\n2. Enter a query like `appname=dhcpd *DHCPDISCOVER* | rex field=message \"DHCPDISCOVER from (?\u003Cmac\u003E[a-fA-F0-9:]+) .*via (?\u003Cinterface\u003E\\S+)\"`\r\n3. Click the search button\r\n\r\n\u003E for the pipe character you will get a line break in the search box.\r\n\u003E if you hit the search button the search box collapses back to show only one line\r\n\r\n# Expected Behavior\r\nAs described before the full query should be visible all the time (or at least 5 rows with an indicator that more rows will be available if there are more than 5 lines of query code). Additional entering a pipe character should not automatically create a line break in the search box.\r\n\r\n# Environment\r\n- Commit Hash: Siglens v0.2.24\r\n- OS: Windows 11\r\n- Browser and Version (if applicable): Edge, current version\r\n\r\n"
# c = "@bernatixer Right now we are sending the Query Link that would fetch the results which caused the Alert to trigger in the latest release.  I believe this is the same as your second suggestion (The ability to run a query over the initial one for the alert data (i.e. get the group by results)). It would look something like this: \r\n\r\n![image](https://github.com/user-attachments/assets/ad33a0b0-f30f-4189-97df-f10b9ce139e1)\r\n\r\n\r\nAlso, are you suggesting that on the UI, the user should be able to configure one of those above for an Alert?"
t = "# Description\r\nMetric alerts show all the metric data into the notification, but it is not readable and brings noise to the alert.\r\nHaving the ability to reduce or tweak the **Alert Data** will allow to have more readable alerts.\r\n\r\n# Benefits\r\nHave more readable alerts and be able to reduce alert noise in the current implementation.\r\n\r\n# Possible Implementations\r\nSome improvements could be:\r\n- The ability to not send metric data on the notification\r\n- The ability to run a query over the initial one for the alert data (i.e. get the group by results)\r\n- The ability to return only the result, not the query+result to reduce alert noise\r\n- - Instead of: `[{temporal_workflow_failed_total{namespace:production.gjvgl,workflow_type:fillLeadWithSmartFieldsWorkflow, 1720096235 1}, ...]`\r\n- -  Return result `[{1}, ...]`\r\n\r\n# Additional Context\r\n\u003Cimg width=\"291\" alt=\"image\" src=\"https://github.com/siglens/siglens/assets/2202231/70f0acd2-5c35-4dc6-9a75-bad51071c612\"\u003E\r\n"


class MarkdownUtil:
    def __init__(self):
        Markdown.output_formats["plain"] = MarkdownUtil._unmark_element

        self._md = Markdown(output_format="plain")
        self._md.stripTopLevelTags = False

    @staticmethod
    def _unmark_element(element, stream=None):
        raise Exception(dir(element))
        if stream is None:
            stream = StringIO()
        if element.text:
            stream.write(element.text)
        for sub in element:
            MarkdownUtil._unmark_element(sub, stream)
        if element.tail:
            stream.write(element.tail)
        return stream.getvalue()

    def md_to_text(self, s):
        html = markdown(t)
        strings = BeautifulSoup(html, features="html.parser").findAll(string=True)
        text = ''.join(strings)
        return text
