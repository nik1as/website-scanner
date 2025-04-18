import asyncio
from importlib.resources import files
from urllib.parse import urlparse

import aiohttp

from website_scanner.info import InformationModule
from website_scanner.utils import get_req_kwargs, is_ip_address, not_none

subdomains_path = files("website_scanner.data").joinpath("subdomains.txt")
with subdomains_path.open("r", encoding="utf-8") as f:
    SUBDOMAINS = [line.strip() for line in f.readlines()]


class Subdomains(InformationModule):

    def __init__(self):
        super().__init__("subdomains")

    async def run(self, session: aiohttp.ClientSession, args):
        if is_ip_address(urlparse(args.url).hostname):
            return

        results = await asyncio.gather(*[self.check_subdomain(session, subdomain, args) for subdomain in SUBDOMAINS])
        return not_none(results)

    @staticmethod
    async def check_subdomain(session: aiohttp.ClientSession, subdomain: str, args):
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
