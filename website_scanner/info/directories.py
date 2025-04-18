import asyncio
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.info import InformationModule
from website_scanner.utils import get_req_kwargs, not_none

directories_path = files("website_scanner.data").joinpath("directories.txt")
with directories_path.open("r", encoding="utf-8") as f:
    DIRECTORIES = [line.strip() for line in f.readlines()]


class Directories(InformationModule):

    def __init__(self):
        super().__init__("directories")

    async def run(self, session: aiohttp.ClientSession, args):
        results = await asyncio.gather(*[self.check_directory(session, args.url, directory, args)
                                         for directory in DIRECTORIES
                                         if f"/{directory}" not in args.ignore])
        return not_none(results)

    @staticmethod
    async def check_directory(session: aiohttp.ClientSession, base_url: str, directory: str, args):
        async with session.get(urljoin(base_url, f"/{directory}"), **get_req_kwargs(args)) as response:
            if response.status != 404:
                return f"/{directory}"
