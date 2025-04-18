import itertools
import re
from urllib.parse import urljoin, urlparse, parse_qsl

import aiohttp
from bs4 import BeautifulSoup

from website_scanner.techs import TechnologyModule
from website_scanner.utils import get_req_kwargs

GENERATOR_REGEX = r"wordpress(?: ([\d.]+))?"


class Wordpress(TechnologyModule):

    def __init__(self):
        super().__init__("wordpress")

    async def run(self, session: aiohttp.ClientSession, args):
        result = {}
        async with session.get(args.url, **get_req_kwargs(args)) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            for tag in soup.find_all("meta", {"name": "generator"}):
                if tag.has_attr("content"):
                    match = re.search(GENERATOR_REGEX, tag.get("content"), re.IGNORECASE)
                    if match is not None:
                        result["version"] = match.group(1)
                        break

            plugins = {}
            hrefs = [tag["href"] for tag in soup.find_all(href=True)]
            srcs = [tag["src"] for tag in soup.find_all(src=True)]
            for ref in itertools.chain(hrefs, srcs):
                parsed = urlparse(ref)
                if parsed.path.startswith("/wp-content/plugins/"):
                    path_split = parsed.path.split("/")
                    if len(path_split) < 4:
                        continue
                    name = path_split[3]
                    version = ""
                    params = dict(parse_qsl(parsed.query))
                    if "ver" in params:
                        version = params["ver"]
                    if name in plugins:
                        if plugins[name] == "":
                            plugins[name] = version
                    else:
                        plugins[name] = version

            result["plugins"] = plugins
            result["xml-rpc"] = await self.check_xmlrpc(session, args)
            result["users"] = await self.enumerate_users(session, args)
            return result

    async def check_xmlrpc(self, session: aiohttp.ClientSession, args):
        async with session.get(urljoin(args.url, "/xmlrpc.php"), **get_req_kwargs(args)) as response:
            if response.status >= 400:
                return "enabled"
        return "disabled"

    async def enumerate_users(self, session: aiohttp.ClientSession, args):
        users = {}
        for user_id in args.wordpress_user_ids:
            async with session.get(urljoin(args.url, f"/?author={user_id}"), **get_req_kwargs(args)) as response:
                html = await response.text()
                name = BeautifulSoup(html, "html.parser").find("title").text.rsplit(" – ", 1)[0]
                if response.status == 200 or 300 <= response.status <= 399:
                    users[user_id] = name
        return users
