import json
import random
import re
import string
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.info import InformationModule

database_path = files("website_scanner.data").joinpath("404.json")
with database_path.open("r", encoding="utf-8") as f:
    DATABASE = json.load(f)


class NotFoundPage(InformationModule):

    def __init__(self):
        super().__init__("not-found-page")

    async def run(self, session: aiohttp.ClientSession, args):
        path = "".join(random.choices(string.ascii_uppercase, k=16))
        url = urljoin(args.url, path)
        async with session.get(url) as response:
            text = await response.text()
            text = re.sub(r"\s+", "", text)
            for framework, fingerprint in DATABASE.items():
                if re.match(fingerprint, text, re.IGNORECASE | re.DOTALL):
                    return framework
