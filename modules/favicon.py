import hashlib
import json
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from modules import Module
from utils import get_req_kwargs

with open("data/favicon-database.json") as f:
    DATABASE = json.load(f)


class Favicon(Module):

    def __init__(self):
        super().__init__("favicon")

    async def run(self, session: aiohttp.ClientSession, args):
        favicon_urls = set()
        async with session.get(args.url, **get_req_kwargs(args)) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            for icon_link_tag in soup.find_all("link", attrs={"rel": "icon", "href": True}):
                favicon_url = urljoin(args.url, icon_link_tag["href"])
                favicon_urls.add(favicon_url)

        if not favicon_urls:
            favicon_urls.add(urljoin(args.url, "favicon.ico"))

        favicon_hashes = []
        for favicon_url in favicon_urls:
            async with session.get(favicon_url, **get_req_kwargs(args)) as response:
                if response.status == 200:
                    favicon_hash = hashlib.md5(await response.read()).hexdigest()
                    for entry in DATABASE:
                        if entry["hash"] == favicon_hash:
                            return entry["name"]
                    favicon_hashes.append(favicon_hash)

        if favicon_hashes:
            return favicon_hashes
