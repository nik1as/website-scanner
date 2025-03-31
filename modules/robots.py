from urllib.parse import urljoin

import aiohttp

from modules import Module
from utils import get_req_kwargs


class Robots(Module):

    def __init__(self):
        super().__init__("robots.txt")

    async def run(self, session: aiohttp.ClientSession, args):
        async with session.get(urljoin(args.url, "/robots.txt"), **get_req_kwargs(args)) as response:
            if response.status == 200:
                text = await response.text()
                lines = [line for line in text.splitlines() if line.strip()]

                allow = []
                disallow = []
                comments = []
                sitemap = []
                for line in lines:
                    if line.startswith("#"):
                        comment = line.lstrip("#").strip()
                        if comment:
                            comments.append(comment)
                    elif line.lower().startswith("allow:"):
                        allow.append(line[6:].strip())
                    elif line.lower().startswith("disallow:"):
                        disallow.append(line[9:].strip())
                    elif line.lower().startswith("sitemap:"):
                        sitemap.append(line[9:].strip())

                result = {}
                if allow:
                    result["allow"] = allow
                if disallow:
                    result["disallow"] = disallow
                if comments:
                    result["comments"] = comments
                if sitemap:
                    result["sitemap"] = sitemap

                return result
