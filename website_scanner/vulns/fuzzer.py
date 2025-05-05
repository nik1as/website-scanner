import asyncio
import itertools
import json
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none, params_to_kwargs
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "fuzz.json")
with payloads_path.open("r", encoding="utf-8") as f:
    PAYLOADS = json.load(f)


class Fuzzer(VulnerabilityModule):

    async def run(self, session: aiohttp.ClientSession, args, directories):
        results = await asyncio.gather(*[self.fuzz_parameters(session, args, directories),
                                         self.omit_parameters(session, args, directories)])
        return list(itertools.chain(*results))

    async def fuzz_parameters(self, session: aiohttp.ClientSession, args, directories):
        tasks = []
        for payload in PAYLOADS:
            for method, directory, params, param in self.get_requests(directories, args.fill):
                tasks.append(self.fuzz_parameter(session, args, method, directory, params, param, payload))
        return not_none(await asyncio.gather(*tasks))

    async def fuzz_parameter(self, session: aiohttp.ClientSession, args, method, directory, params, param, payload):
        try:
            async with session.request(method, urljoin(args.url, directory), **params_to_kwargs(method, params)) as response:
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "directory": directory, "param": param, "payload": payload}
        except:
            pass

    async def omit_parameters(self, session: aiohttp.ClientSession, args, directories):
        tasks = []
        for method, directory, params, param, in self.get_requests(directories, args.fill):
            params.pop(param)
            tasks.append(self.check_parameter_combination(session, args, method, directory, params, param))

        return not_none(await asyncio.gather(*tasks))

    async def check_parameter_combination(self, session: aiohttp.ClientSession, args, method, directory, params, omit):
        try:
            async with session.request(method, urljoin(args.url, directory), **params_to_kwargs(method, params)) as response:
                if response.status >= 500:
                    return {"type": "Omit-Parameter", "status": response.status, "method": method, "directory": directory, "payload": omit}
        except:
            pass
