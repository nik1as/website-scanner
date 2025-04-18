import itertools
import json
import re
from collections import defaultdict
from importlib.resources import files
from itertools import takewhile

import aiohttp
from bs4 import BeautifulSoup

from website_scanner.modules import Module
from website_scanner.utils import get_req_kwargs, set_cpe_version

technologies_path = files("website_scanner.data").joinpath("technologies.json")
with technologies_path.open("r", encoding="utf-8") as f:
    TECHNOLOGIES = json.load(f)

categories_path = files("website_scanner.data").joinpath("categories.json")
with categories_path.open("r", encoding="utf-8") as f:
    CATEGORIES = json.load(f)


def search(value: str, pattern: str) -> tuple[bool, str | None, int]:
    if isinstance(value, bytes):
        value = value.decode()

    split = re.split(r"\\;", pattern)
    regex = split[0]
    version_group = None
    confidence = 100
    for tag in split[1:]:
        if tag.startswith(r"version:"):
            try:
                version_group = int("".join(takewhile(str.isdigit, tag[9:].strip())))
            except ValueError:
                pass
        elif tag.startswith(r"confidence:"):
            try:
                confidence = int(tag[11:].strip())
            except ValueError:
                pass

    match = re.search(regex, value, re.IGNORECASE)

    if match is None:
        return False, None, 0

    if version_group is None:
        version = None
    else:
        version = match.group(version_group)

    return True, version, confidence


def detect(spec, response, html, soup) -> tuple[bool, int, set[str]]:
    match = False
    total_confidence = 0
    versions = set()

    for key, pattern in spec.get("headers", dict()).items():
        value = response.headers.get(key)
        if value is not None:
            found, version, confidence = search(value, pattern)
            if found:
                match = True
                total_confidence += confidence
                if version is not None:
                    versions.add(version)

    for key, pattern in spec.get("cookies", dict()).items():
        value = response.cookies.get(key)
        if value is not None:
            found, version, confidence = search(value, pattern)
            if found:
                match = True
                total_confidence += confidence
                if version is not None:
                    versions.add(version)

    for pattern in spec.get("html", []):
        found, version, confidence = search(html, pattern)
        if found:
            match = True
            total_confidence += confidence
            if version is not None:
                versions.add(version)

    script_src = [tag["src"] for tag in soup.findAll("script", attrs={"src": True})]
    for pattern in spec.get("scriptSrc", []):
        for src in script_src:
            found, version, confidence = search(src, pattern)
            if found:
                match = True
                total_confidence += confidence
                if version is not None:
                    versions.add(version)

    meta = {meta["name"].lower(): meta["content"] for meta in soup.findAll("meta", attrs={"name": True, "content": True})}
    for key, pattern in spec.get("meta", dict()).items():
        value = meta.get(key)
        if value is not None:
            found, version, confidence = search(value, pattern)
            if found:
                match = True
                total_confidence += confidence
                if version is not None:
                    versions.add(version)

    return match, min(total_confidence, 100), versions


class Technology(Module):

    def __init__(self):
        super().__init__("technology")

    async def run(self, session: aiohttp.ClientSession, args):
        async with session.get(args.url, **get_req_kwargs(args)) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            detected = []
            for name, spec in TECHNOLOGIES.items():
                match, confidence, versions = detect(spec, response, html, soup)
                if not match:
                    continue
                if confidence < args.confidence_threshold:
                    continue
                version = max(versions, key=len) if versions else None
                if match:
                    detected.append({
                        "name": name,
                        "version": version,
                        "cpe": spec.get("cpe"),
                        "website": spec.get("website"),
                        "description": spec.get("description"),

                        "cats": spec.get("cats", []),
                        "implies": spec.get("implies", []),
                        "requires": spec.get("requires", []),
                    })

            tech_names = {element["name"] for element in detected}
            implied = set(itertools.chain(*[element["implies"] for element in detected]))
            while implied:
                imply_name = implied.pop()
                if imply_name in tech_names:
                    continue
                spec = TECHNOLOGIES[imply_name]
                detected.append({
                    "name": imply_name,
                    "version": None,
                    "cpe": spec.get("cpe"),
                    "website": spec.get("website"),
                    "description": spec.get("description"),

                    "cats": spec.get("cats", []),
                    "implies": spec.get("implies", []),
                    "requires": spec.get("requires", []),
                })
                tech_names.add(imply_name)
                implied.update(spec.get("implies", []))

            result = defaultdict(dict)
            tech_names = {element["name"] for element in detected}
            for element in detected:
                if any(requirement not in tech_names for requirement in element["requires"]):
                    continue

                tech_result = dict()
                if element["version"] is not None:
                    tech_result["version"] = element["version"]
                    if element["cpe"] is not None:
                        tech_result["cpe"] = set_cpe_version(element["cpe"], element["version"])
                if element["website"] is not None:
                    tech_result["website"] = element["website"]
                if element["description"] is not None:
                    tech_result["description"] = element["description"]

                for category in [CATEGORIES[str(cat_id)]["name"] for cat_id in element["cats"]]:
                    result[category][element["name"]] = tech_result

            return result
