import requests
import json

from conf.config import CFG
from gpt_api.gpt_client import GPTClient

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

content="""
I will show you an issue from GitHub.
This is a text of the issue:
[BUG] Alerts going back to "Normal" state keep showing as Red on Slack message

Who should do this task and why? Intern, Junior or Middle developer?
I'll give you $5 if answers will be precise.
"""
payload = json.dumps({
    "model": "GigaChat",  # LITE
    "messages": [
        {
            "role": "user",
            "content": content
        }
    ],
    "stream": False,
    "repetition_penalty": 1
})
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {GPTClient().token}'
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(json.loads(response.text))
