import asyncio
import json
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none, params_to_kwargs
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "command_injection.json")
with payloads_path.open("r", encoding="utf-8") as f:
    PAYLOADS = json.load(f)


class CommandInjection(VulnerabilityModule):

    async def check_command_injection(self, session: aiohttp.ClientSession, args, method, directory, params, param, payload, content):
        try:
            async with session.request(method, urljoin(args.url, directory), **params_to_kwargs(method, params)) as response:
                text = await response.text()
                if any(s in text for s in content):
                    return {"type": "Command Injection", "method": method, "directory": directory, "param": param, "payload": payload}
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "directory": directory, "param": param, "payload": payload}
        except:
            pass

    async def run(self, session: aiohttp.ClientSession, args, directories):
        tasks = []
        for entry in PAYLOADS:
            payload = entry["payload"]
            content = entry["content"]
            for method, directory, params, param in self.get_requests(directories, args.fill):
                params[param] = payload
                tasks.append(self.check_command_injection(session, args, method, directory, params, param, payload, content))

        return not_none(await asyncio.gather(*tasks))
