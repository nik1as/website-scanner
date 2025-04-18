import configparser
from urllib.parse import urljoin

import aiohttp

from website_scanner.modules import Module
from website_scanner.utils import get_req_kwargs


class Git(Module):

    def __init__(self):
        super().__init__("git")

    async def run(self, session: aiohttp.ClientSession, args):
        result = dict()
        async with session.get(urljoin(args.url, "/.git/"), **get_req_kwargs(args)) as response:
            if response.status == 200:
                result["status"] = "found"
            else:
                return

        async with session.get(urljoin(args.url, "/.git/description"), **get_req_kwargs(args)) as response:
            if response.status == 200:
                result["description"] = (await response.text()).strip()

        async with session.get(urljoin(args.url, "/.git/config"), **get_req_kwargs(args)) as response:
            if response.status == 200:
                config = configparser.ConfigParser()
                config.read_string(await response.text())

                try:
                    remote_url = config["remote \"origin\""]["url"]
                    result["remote"] = remote_url
                except KeyError:
                    pass

        async with session.get(urljoin(args.url, "/.git/logs/HEAD"), **get_req_kwargs(args)) as response:
            if response.status == 200:
                commits = []
                text = (await response.text()).strip()
                for line in text.splitlines():
                    parts = line.split()
                    if len(parts) < 7:
                        continue  # skip malformed lines

                    commit_hash = parts[1]
                    author = parts[2]
                    message = " ".join(parts[6:])

                    commits.append({"hash": commit_hash, "author": author, "message": message})
                result["commits"] = commits

        return result
