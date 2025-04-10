import asyncio
import hashlib
import sys
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup


async def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        exit()

    async with aiohttp.ClientSession() as session:
        url = sys.argv[1]
        favicon_urls = set()
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            for icon_link_tag in soup.find_all("link", attrs={"rel": "icon", "href": True}):
                favicon_url = urljoin(url, icon_link_tag["href"])
                favicon_urls.add(favicon_url)

        if not favicon_urls:
            favicon_urls.add(urljoin(url, "favicon.ico"))

        print(", ".join(favicon_urls))

        for favicon_url in favicon_urls:
            async with session.get(favicon_url) as response:
                if response.status == 200:
                    favicon_hash = hashlib.md5(await response.read()).hexdigest()
                    print(favicon_hash)


if __name__ == "__main__":
    asyncio.run(main())
