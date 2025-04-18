import asyncio

import aiohttp

from website_scanner.info import InformationModule
from website_scanner.utils import get_req_kwargs, not_none

METHODS = ["get", "post", "put", "delete", "head", "options", "patch"]


class Methods(InformationModule):

    def __init__(self):
        super().__init__("methods")

    async def run(self, session: aiohttp.ClientSession, args):
        results = await asyncio.gather(*[self.check_method(session, method, args) for method in METHODS])
        return not_none(results)

    @staticmethod
    async def check_method(session: aiohttp.ClientSession, method: str, args):
        try:
            async with session.request(method, args.url, **get_req_kwargs(args)) as response:
                if response.status not in (405, 501):
                    return method
        except aiohttp.ServerDisconnectedError:
            pass
