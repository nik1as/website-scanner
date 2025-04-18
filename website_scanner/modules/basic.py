import aiohttp
from bs4 import BeautifulSoup

from website_scanner.modules import Module
from website_scanner.utils import get_req_kwargs


class Basic(Module):

    def __init__(self):
        super().__init__("basic")

    async def run(self, session: aiohttp.ClientSession, args):
        async with session.get(args.url, allow_redirects=True, **get_req_kwargs(args)) as response:
            result = dict()

            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            if soup.title:
                result["title"] = soup.title.string

            generator_tag = soup.find("meta", attrs={"name": "generator"})
            if generator_tag and "content" in generator_tag.attrs:
                result["generator"] = generator_tag["content"]

            if response.history:
                result["redirect"] = str(response.url)

            return result
