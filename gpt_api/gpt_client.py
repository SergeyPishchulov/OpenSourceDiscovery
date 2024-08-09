import json
import uuid
from collections import namedtuple
from datetime import datetime, timezone
from typing import NamedTuple

import aiohttp
import requests

from conf.config import CFG


class GigaToken(NamedTuple):
    access_token: str
    expires_at: datetime


class GPTClient:
    def __init__(self):
        self._token = None

    @property
    def token(self) -> str:
        if self._token is None or self._token.expires_at < datetime.now():
            self._token = self.generate_access_token()
        return self._token.access_token

    def generate_access_token(self) -> GigaToken:
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        payload = 'scope=GIGACHAT_API_PERS'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {CFG.gigachat.auth_data}'
        }

        response = requests.request("POST", url,
                                    headers=headers, data=payload, verify=False)
        j = json.loads(response.text)
        ts = round(j['expires_at'] / 1000)
        token = GigaToken(access_token=j['access_token'],
                          expires_at=datetime.fromtimestamp(ts)
                          )
        return token

    async def send(self, content: str):
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

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
            'Authorization': f'Bearer {self.token}'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload, verify_ssl=False) as response:
                text = await response.text()
                d = json.loads(text)
                return self.parse_response(d)


    def parse_response(self, d:dict):
        # raise Exception(d)
        c = d["choices"][0]["message"]["content"]
        if "small" in c:
            return "small"
        if "medium" in c:
            return "medium"
        if "big" in c:
            return "big"
