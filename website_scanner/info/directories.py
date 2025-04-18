import asyncio
import itertools
from importlib.resources import files
from urllib.parse import urljoin, urlparse

import aiohttp

from website_scanner.info import InformationModule

directories_path = files("website_scanner.data").joinpath("directories.txt")
with directories_path.open("r", encoding="utf-8") as f:
    DIRECTORIES = [line.strip() for line in f.readlines()]


class Directories(InformationModule):

    def __init__(self):
        super().__init__("directories")

    async def run(self, session: aiohttp.ClientSession, args):
        results = await asyncio.gather(*[self.check_directory(session, new_url, args.depth, args)
                                         for new_url in self.get_urls(args.url, args.extensions, args.ignore)])
        return list(itertools.chain(*results))

    async def check_directory(self, session: aiohttp.ClientSession, url: str, depth: int, args) -> list[str]:
        async with session.get(url) as response:
            if response.status != 404:
                directories = [urlparse(url).path]
                if args.recursive and depth - 1 > 0:
                    tasks = [self.check_directory(session, new_url, depth - 1, args) for new_url in self.get_urls(url, args.extensions, args.ignore)]
                    directories.extend(itertools.chain(*(await asyncio.gather(*tasks))))
                return directories
        return []

    @staticmethod
    def get_urls(curr_url: str, extensions: list[str], ignore: list[str]) -> list:
        for word in DIRECTORIES:
            new_url = urljoin(curr_url, f"{word}/")
            path = urlparse(new_url).path
            if path not in ignore:
                yield new_url

        for ext in extensions:
            for word in DIRECTORIES:
                new_url = urljoin(curr_url, f"{word}.{ext.lstrip('.')}")
                path = urlparse(new_url).path
                if path not in ignore:
                    yield new_url
