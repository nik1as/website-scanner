import asyncio
import json
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "xss.json")
with payloads_path.open("r", encoding="utf-8") as f:
    PAYLOADS = json.load(f)


class XSS(VulnerabilityModule):

    async def check_xss(self, session: aiohttp.ClientSession, args, method, path, params, param, payload):
        try:
            params_kwargs = {"params": params} if method == "get" else {"data": params}

            async with session.request(method, urljoin(args.url, path), **params_kwargs) as response:
                text = await response.text()
                content_type = response.headers["Content-Type"].split(";")[0].strip()
                if payload in text and content_type == "text/html":
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
