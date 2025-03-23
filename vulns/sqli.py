import asyncio
import json
from urllib.parse import urljoin

import aiohttp

from utils import not_none
from vulns import VulnerabilityModule

with open("data/payloads/sqli.json") as f:
    PAYLOADS = json.load(f)


class SQLI(VulnerabilityModule):

    async def check_error_based(self, session: aiohttp.ClientSession, args, method, path, params, param, payload):
        try:
            params_kwargs = {"params": params} if method == "get" else {"data": params}

            async with session.request(method, urljoin(args.url, path), **params_kwargs) as response:
                text = await response.text()
                text = text.casefold()
                if any(msg in text for msg in PAYLOADS["error-based"]["messages"]):
                    return {"type": "SQL-Injection (error-based)", "method": method, "path": path, "param": param, "payload": payload}
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "path": path, "param": param, "payload": payload}
        except:
            pass

    async def error_based(self, session: aiohttp.ClientSession, args, dirs):
        tasks = []
        for method, path, params, param, payload in self.get_requests(dirs, PAYLOADS["error-based"]["payloads"]):
            tasks.append(self.check_error_based(session, args, method, path, params, param, payload))

        return not_none(await asyncio.gather(*tasks))

    async def run(self, session: aiohttp.ClientSession, args, dirs):
        return await self.error_based(session, args, dirs)
