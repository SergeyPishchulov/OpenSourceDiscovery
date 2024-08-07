import requests
import json

from conf.config import CFG
from gpt_api.gpt_client import GPTClient

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

payload = json.dumps({
    "model": "GigaChat",  # LITE
    "messages": [
        {
            "role": "user",
            "content": "I will show you a message. Tell me is it positive or negative. The message is 'Glad to hear you'"
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
