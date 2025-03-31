import asyncio
import re
from collections import defaultdict
from urllib.parse import urlparse, parse_qs, urljoin

import aiohttp
from bs4 import BeautifulSoup

from modules import Module
from regex import HTML_COMMENT_REGEX, HTTP_URL_REGEX, EMAIL_REGEX
from utils import parse_form, get_req_kwargs


class Directory:

    def __init__(self, directory: str):
        self.directory = directory
        self.url_parameters = defaultdict(set)
        self.post_parameters = defaultdict(set)

    def json(self):
        result = dict()
        if self.url_parameters:
            result["url-parameters"] = {k: list(v) if len(v) > 1 else list(v)[0] for k, v in self.url_parameters.items()}
        if self.post_parameters:
            result["post-parameters"] = {k: list(v) if len(v) > 1 else list(v)[0] for k, v in self.post_parameters.items()}
        return result


class Crawler(Module):

    def __init__(self):
        super().__init__("crawler")

    async def run(self, session: aiohttp.ClientSession, args):
        directories = dict()
        emails = set()
        comments = set()

        def add_to_directories(href: str, curr_url: str):
            new_url = href
            if re.match(HTTP_URL_REGEX, href):
                href_domain = urlparse(href).netloc
                if href_domain != urlparse(curr_url).netloc:
                    return
            else:
                new_url = urljoin(curr_url, href)

            parsed = urlparse(new_url)
            if parsed.path in args.ignore:
                return
            if parsed.scheme not in ["http", "https"]:
                return
            if parsed.path not in directories:
                directory = Directory(parsed.path)
                directories[parsed.path] = directory
                return new_url
            else:
                directory = directories[parsed.path]

            new_param = False
            for key, values in parse_qs(parsed.query).items():
                if any(v not in directory.url_parameters[key] for v in values):
                    new_param = True
                directory.url_parameters[key].update(values)
            if new_param:
                return new_url

        async def crawl(curr_url: str, depth: int):
            if depth > args.depth:
                return

            try:
                async with session.get(curr_url, **get_req_kwargs(args), allow_redirects=False) as response:
                    try:
                        html = await response.text()
                    except UnicodeDecodeError:
                        return

                    soup = BeautifulSoup(html, "html.parser")

                    for match in EMAIL_REGEX.findall(html):
                        emails.add(match)
                    for match in HTML_COMMENT_REGEX.findall(html):
                        comments.add(match.strip())
                    for form in soup.find_all("form"):
                        method, action, params = parse_form(form)
                        path = urlparse(urljoin(curr_url, action)).path

                        if path not in directories:
                            directory = Directory(path)
                            directories[path] = directory
                        else:
                            directory = directories[path]

                        for name, value in params.items():
                            if method.casefold() == "post":
                                directory.post_parameters[name].add(value)
                            elif method.casefold() == "get":
                                directory.url_parameters[name].add(value)

                    urls = set()

                    if "Location" in response.headers:
                        location = response.headers["Location"]
                        new_url = add_to_directories(location, curr_url)
                        if new_url is not None:
                            urls.add(new_url)

                    for link in soup.find_all("a"):
                        href = link.get("href")
                        if href is None:
                            continue
                        new_url = add_to_directories(href, curr_url)
                        if new_url is not None:
                            urls.add(new_url)

                    await asyncio.gather(*[crawl(new_url, depth + 1) for new_url in urls])
            except (aiohttp.ClientError, asyncio.TimeoutError):
                pass

        add_to_directories("", args.url)

        await crawl(args.url, 1)

        result = {"directories": {d.directory: d.json() for d in directories.values()}}
        if emails:
            result["emails"] = list(emails)
        if comments:
            result["comments"] = list(comments)

        return result
