import aiohttp

from website_scanner.modules import Module
from website_scanner.utils import get_req_kwargs


class CookieFlag(Module):

    def __init__(self):
        super().__init__("cookies")

    async def run(self, session: aiohttp.ClientSession, args):
        async with session.get(args.url, **get_req_kwargs(args)) as response:
            result = dict()
            for cookie in response.cookies.values():
                result[cookie.key] = {
                    "name": cookie.key,
                    "value": cookie.value,
                    "secure": cookie["secure"] or False,
                    "httponly": cookie["httponly"] or False,
                }

            return result
