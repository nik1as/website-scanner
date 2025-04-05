import asyncio
from urllib.parse import urlparse

import aiohttp

from modules import Module
from utils import get_req_kwargs

with open("data/subdomains.txt", "r") as f:
    SUBDOMAINS = [line.strip() for line in f.readlines()]


class Subdomains(Module):

    def __init__(self):
        super().__init__("subdomains")

    async def check(self, session: aiohttp.ClientSession, subdomain: str, args):
        try:
            parsed = urlparse(args.url)
            port = parsed.port
            if port is None:
                host = f"{subdomain}.{parsed.hostname}"
            else:
                host = f"{subdomain}.{parsed.hostname}:{port}"

            async with session.get(args.url, headers={"Host": host}, allow_redirects=False, **get_req_kwargs(args)) as response:
                if response.status == 200:
                    return host
        except:
            return

    async def run(self, session: aiohttp.ClientSession, args):
        results = await asyncio.gather(*[self.check(session, subdomain, args) for subdomain in SUBDOMAINS])
        return [result for result in results if result is not None]
