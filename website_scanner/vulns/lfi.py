import asyncio
import json
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none, params_to_kwargs
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "lfi.json")
with payloads_path.open("r", encoding="utf-8") as f:
    PAYLOADS = json.load(f)


class LFI(VulnerabilityModule):

    async def check_lfi(self, session: aiohttp.ClientSession, args, method, directory, params, param, payload, content):
        try:
            async with session.request(method, urljoin(args.url, directory), **params_to_kwargs(method, params)) as response:
                text = await response.text()
                if any(s in text for s in content):
                    return {"type": "LFI", "method": method, "directory": directory, "param": param, "payload": payload}
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "directory": directory, "param": param, "payload": payload}
        except:
            pass

    def get_file_paths(self, args):
        for os in PAYLOADS:
            for parent, sep in PAYLOADS[os]["separators"]:
                for file in PAYLOADS[os]["files"]:
                    for d in range(1, args.lfi_depth + 1):
                        path = (parent + sep) * d + sep.join(file["path"])
                        yield path, file["content"]

    async def run(self, session: aiohttp.ClientSession, args, directories):
        tasks = []
        payloads = list(self.get_file_paths(args))

        for file_path, content in payloads:
            for method, directory, params, param, in self.get_requests(directories, args.fill):
                params[param] = file_path
                tasks.append(self.check_lfi(session, args, method, directory, params, param, file_path, content))

        return not_none(await asyncio.gather(*tasks))
