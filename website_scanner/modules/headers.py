import aiohttp

from website_scanner.modules import Module
from website_scanner.utils import get_req_kwargs

INTERESTING_HEADERS = ["Server", "X-Powered-By", "Via", "X-AspNet-Version", "X-Backend-Server", "X-Powered-CMS", "X-PHP-Version", "X-Drupal-Cache",
                       "X-Joomla-Version", "X-Generator", "X-Content-Type-Options", "X-XSS-Protection", "X-Frame-Options", "Content-Security-Policy",
                       "Strict-Transport-Security", "X-Runtime", "X-Version", "X-Cache", "X-Backend"]


class Headers(Module):

    def __init__(self):
        super().__init__("headers")

    async def run(self, session: aiohttp.ClientSession, args):
        async with session.get(args.url, **get_req_kwargs(args)) as response:
            result = dict()
            for header in INTERESTING_HEADERS:
                if header in response.headers:
                    result[header] = response.headers.get(header)
            return result
