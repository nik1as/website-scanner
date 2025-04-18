import asyncio
import json
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "command_injection.json")
with payloads_path.open("r", encoding="utf-8") as f:
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
