import asyncio
import json
import string

import aiohttp
import yaml


async def fetch_technologies(session: aiohttp.ClientSession, name: str) -> dict:
    async with session.get(f"https://raw.githubusercontent.com/enthec/webappanalyzer/main/src/technologies/{name}.json") as response:
        return await response.json(content_type="text/plain")


async def download_technology_database(session: aiohttp.ClientSession):
    file_names = list(string.ascii_lowercase + "_")
    files = await asyncio.gather(*[fetch_technologies(session, name) for name in file_names])

    database = dict()
    for data in files:
        for key, value in data.items():
            database[key] = value

    with open("technologies.json", "w") as f:
        json.dump(database, f)


async def download_favicon_database(session: aiohttp.ClientSession):
    async with session.get("https://raw.githubusercontent.com/OWASP/www-community/refs/heads/master/_data/favicons-database.yml") as response:
        data = yaml.safe_load(await response.text())
        with open(f"favicons.json", "w") as f:
            json.dump(data, f)


async def main():
    async with aiohttp.ClientSession() as session:
        await download_technology_database(session)
        await download_favicon_database(session)


if __name__ == "__main__":
    asyncio.run(main())
