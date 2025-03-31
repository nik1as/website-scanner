import json
import re

import aiohttp
from bs4 import BeautifulSoup

from modules import Module
from utils import get_req_kwargs

NO_VERSION_FOUND = " "

with open("data/technologies.json", "r") as f:
    TECHNOLOGIES = json.load(f)
with open("data/categories.json", "r") as f:
    CATEGORIES = json.load(f)


def search(value, regex):
    if isinstance(value, bytes):
        value = value.decode()

    split = re.split(r"\\;version:\\", regex)
    regex = split[0]
    group = None
    if len(split) > 1:
        try:
            group = int(split[1])
        except ValueError:
            pass

    return re.search(regex, value, re.IGNORECASE), group


def match_dict(patterns, values):
    version = None
    for key, pattern in patterns.items():
        value = values.get(key)
        if value is not None:
            match, group = search(value, pattern)
            if match is not None:
                if group is not None:
                    version = match.group(group)
                elif version is None:
                    version = NO_VERSION_FOUND
    return version


def match_list(patterns, values):
    version = None

    if not isinstance(patterns, list):
        patterns = [patterns]
    if not isinstance(values, list):
        values = [values]

    for pattern in patterns:
        for value in values:
            match, group = search(value, pattern)
            if match is not None:
                if group is not None:
                    version = match.group(group)
                elif version is None:
                    version = NO_VERSION_FOUND
    return version


def get_categories(spec):
    return [CATEGORIES[str(c_id)]["name"] for c_id in spec["cats"]]


def add_app(techs, name, version, spec):
    for category in get_categories(spec):
        if category not in techs:
            techs[category] = dict()
        if name not in techs[category]:
            techs[category][name] = version
            implies = spec.get("implies", [])
            if not isinstance(implies, list):
                implies = [implies]
            for app_name in implies:
                add_app(techs, app_name, NO_VERSION_FOUND, TECHNOLOGIES[app_name])
        elif techs[category][name] == NO_VERSION_FOUND:
            techs[category][name] = version


class Technology(Module):

    def __init__(self):
        super().__init__("technology")

    async def run(self, session: aiohttp.ClientSession, args):
        async with session.get(args.url, **get_req_kwargs(args)) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            results = dict()
            for name, spec in TECHNOLOGIES.items():
                version = match_dict(spec.get("headers", dict()), response.headers)
                if version is not None:
                    add_app(results, name, version, spec)

                version = match_dict(spec.get("cookies", dict()), response.cookies)
                if version is not None:
                    add_app(results, name, version, spec)

                version = match_list(spec.get("html", []), html)
                if version is not None:
                    add_app(results, name, version, spec)

                script_src = [tag["src"] for tag in soup.findAll('script', {"src": True})]
                version = match_list(spec.get("scriptSrc", []), script_src)
                if version is not None:
                    add_app(results, name, version, spec)

            return results
