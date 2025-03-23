import asyncio
import json
from urllib.parse import urljoin

import aiohttp

from utils import not_none
from vulns import VulnerabilityModule

with open("data/payloads/xss.json") as f:
    PAYLOADS = json.load(f)


class XSS(VulnerabilityModule):

    async def check_xss(self, session: aiohttp.ClientSession, args, method, path, params, param, payload):
        try:
            params_kwargs = {"params": params} if method == "get" else {"data": params}

            async with session.request(method, urljoin(args.url, path), **params_kwargs) as response:
                text = await response.text()
                if payload in text:
                    return {"type": "XSS", "method": method, "path": path, "param": param, "payload": payload}
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "path": path, "param": param, "payload": payload}
        except:
            pass

    async def run(self, session: aiohttp.ClientSession, args, dirs):
        tasks = []
        for method, path, params, param, payload in self.get_requests(dirs, PAYLOADS):
            tasks.append(self.check_xss(session, args, method, path, params, param, payload))

        return not_none(await asyncio.gather(*tasks))
