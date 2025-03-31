import asyncio
import json
from urllib.parse import urljoin

import aiohttp

from utils import not_none
from vulns import VulnerabilityModule

with open("data/payloads/command_injection.json") as f:
    PAYLOADS = json.load(f)


class CommandInjection(VulnerabilityModule):

    async def check_command_injection(self, session: aiohttp.ClientSession, args, method, path, params, param, payload, content):
        try:
            params_kwargs = {"params": params} if method == "get" else {"data": params}

            async with session.request(method, urljoin(args.url, path), **params_kwargs) as response:
                text = await response.text()
                if any(s in text for s in content):
                    return {"type": "Command Injection", "method": method, "path": path, "param": param, "payload": payload}
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "path": path, "param": param, "payload": payload}
        except:
            pass

    async def run(self, session: aiohttp.ClientSession, args, dirs):
        tasks = []
        for entry in PAYLOADS:
            payload = entry["payload"]
            content = entry["content"]
            for method, path, params, param, _ in self.get_requests(dirs, [""]):
                params[param] = payload
                tasks.append(self.check_command_injection(session, args, method, path, params, param, payload, content))

        return not_none(await asyncio.gather(*tasks))
