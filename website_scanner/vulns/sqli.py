import asyncio
import json
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none, params_to_kwargs
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "sqli.json")
with payloads_path.open("r", encoding="utf-8") as f:
    PAYLOADS = json.load(f)


class SQLI(VulnerabilityModule):

    async def check_error_based(self, session: aiohttp.ClientSession, args, method, directory, params, param, payload):
        try:
            async with session.request(method, urljoin(args.url, directory), **params_to_kwargs(method, params)) as response:
                text = await response.text()
                text = text.casefold()
                if any(msg in text for msg in PAYLOADS["error-based"]["messages"]):
                    return {"type": "SQL-Injection (error-based)", "method": method, "directory": directory, "param": param, "payload": payload}
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "directory": directory, "param": param, "payload": payload}
        except:
            pass

    async def error_based(self, session: aiohttp.ClientSession, args, directories):
        tasks = []
        for payload in PAYLOADS["error-based"]["payloads"]:
            for method, directory, params, param in self.get_requests(directories, args.fill):
                params[param] = payload
                tasks.append(self.check_error_based(session, args, method, directory, params, param, payload))

        return not_none(await asyncio.gather(*tasks))

    async def run(self, session: aiohttp.ClientSession, args, directories):
        return await self.error_based(session, args, directories)
