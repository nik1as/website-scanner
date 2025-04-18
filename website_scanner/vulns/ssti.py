import asyncio
import json
import random
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "ssti.json")
with payloads_path.open("r", encoding="utf-8") as f:
    PAYLOADS = json.load(f)


class SST(VulnerabilityModule):

    async def check_ssti(self, session: aiohttp.ClientSession, args, method, path, params, param, payload, num):
        try:
            params_kwargs = {"params": params} if method == "get" else {"data": params}

            async with session.request(method, urljoin(args.url, path), **params_kwargs) as response:
                text = await response.text()
                if str(num * num) in text:
                    return {"type": "SSTI", "method": method, "path": path, "param": param, "payload": payload}
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "path": path, "param": param, "payload": payload}
        except:
            pass

    async def run(self, session: aiohttp.ClientSession, args, dirs):
        num = random.randint(1_000, 100_000)
        payloads = [p.replace("x", str(num)) for p in PAYLOADS]

        tasks = []
        for method, path, params, param, payload in self.get_requests(dirs, payloads):
            tasks.append(self.check_ssti(session, args, method, path, params, param, payload, num))

        return not_none(await asyncio.gather(*tasks))
