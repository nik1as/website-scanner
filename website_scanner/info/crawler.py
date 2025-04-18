import asyncio
from collections import defaultdict
from urllib.parse import urlparse, parse_qs, urljoin

import aiohttp
from bs4 import BeautifulSoup

from website_scanner.info import InformationModule
from website_scanner.regex import EMAIL_REGEX, HTML_COMMENT_REGEX
from website_scanner.utils import parse_form, get_req_kwargs


class Directory:

    def __init__(self, directory: str):
        self.directory = directory
        self.url_parameters = defaultdict(set)
        self.post_parameters = defaultdict(set)

    def add_parameters(self, method: str, params: dict = None) -> bool:
        if params is None:
            return False
        if method.casefold() == "get":
            return self.add_query_parameters("&".join(f"{key}={value}" for key, value in params.items()))
        if method.casefold() == "post":
            return self.add_post_parameters(params)

    def add_query_parameters(self, query: str) -> bool:
        new_param = False
        for key, values in parse_qs(query).items():
            if any(v not in self.url_parameters[key] for v in values):
                new_param = True
            self.url_parameters[key].update(values)
        return new_param

    def add_post_parameters(self, params: dict[str, str]) -> bool:
        new_param = False
        for key, value in params.items():
            if value not in self.post_parameters[key]:
                new_param = True
            self.post_parameters[key].add(value)
        return new_param

    def json(self):
        result = dict()
        if self.url_parameters:
            result["url-parameters"] = {k: list(v) if len(v) > 1 else list(v)[0] for k, v in self.url_parameters.items()}
        if self.post_parameters:
            result["post-parameters"] = {k: list(v) if len(v) > 1 else list(v)[0] for k, v in self.post_parameters.items()}
        return result


class Crawler(InformationModule):

    def __init__(self):
        super().__init__("crawler")

    async def run(self, session: aiohttp.ClientSession, args):
        directories = dict()
        emails = set()
        comments = set()

        def add_to_directories(method: str, href: str, curr_url: str, params: dict = None) -> str | None:
            new_url = urljoin(curr_url, href)
            parsed = urlparse(new_url)

            if (parsed.netloc != urlparse(curr_url).netloc) or (parsed.path in args.ignore) or (parsed.scheme not in ["http", "https"]):
                return

            if parsed.path in directories:
                directory = directories[parsed.path]
                new_param = directory.add_query_parameters(parsed.query)
                new_param = new_param or directory.add_parameters(method, params)
                if new_param:
                    return new_url
            else:
                directory = Directory(parsed.path)
                directory.add_query_parameters(parsed.query)
                directory.add_parameters(method, params)
                directories[parsed.path] = directory
                return new_url

        async def crawl(method: str, curr_url: str, params: dict[str, str], depth: int):
            if depth > args.depth:
                return

            crawl_tasks = []
            try:
                params_kwargs = {"params": params} if method == "get" else {"data": params}
                async with session.request(method, curr_url, **params_kwargs, **get_req_kwargs(args), allow_redirects=False) as response:
                    if response.status == 404:
                        return

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
                        form_method, form_action, form_params = parse_form(form)
                        new_url = add_to_directories(form_method, form_action, curr_url, form_params)
                        if new_url is not None:
                            crawl_tasks.append(crawl(form_method, new_url, form_params, depth + 1))

                    if "Location" in response.headers:
                        location = response.headers["Location"]
                        new_url = add_to_directories("get", location, curr_url)
                        if new_url is not None:
                            crawl_tasks.append(crawl("get", new_url, dict(), depth + 1, ))

                    for link in soup.find_all("a"):
                        href = link.get("href")
                        if href is None:
                            continue
                        new_url = add_to_directories("get", href, curr_url)
                        if new_url is not None:
                            crawl_tasks.append(crawl("get", new_url, dict(), depth + 1))

                    await asyncio.gather(*crawl_tasks)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                pass

        add_to_directories("get", "", args.url)

        await crawl("get", args.url, dict(), 1)

        result = {"directories": {d.directory: d.json() for d in directories.values()}}
        if emails:
            result["emails"] = list(emails)
        if comments:
            result["comments"] = list(comments)

        return result
