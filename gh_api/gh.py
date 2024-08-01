import aiohttp


class GHClient:
    async def get_repo(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()


