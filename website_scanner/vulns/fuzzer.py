import asyncio
import itertools
import json
from importlib.resources import files
from urllib.parse import urljoin

import aiohttp

from website_scanner.utils import not_none
from website_scanner.vulns import VulnerabilityModule

payloads_path = files("website_scanner.data").joinpath("payloads", "fuzz.json")
with payloads_path.open("r", encoding="utf-8") as f:
    PAYLOADS = json.load(f)


class Fuzzer(VulnerabilityModule):

    async def run(self, session: aiohttp.ClientSession, args, dirs):
        results = await asyncio.gather(*[self.fuzz_parameters(session, args, dirs),
                                         self.omit_parameters(session, args, dirs)])
        return list(itertools.chain(*results))

    async def fuzz_parameters(self, session: aiohttp.ClientSession, args, dirs):
        tasks = []
        for method, path, params, param, payload in self.get_requests(dirs, PAYLOADS):
            tasks.append(self.fuzz_parameter(session, args, method, path, params, param, payload))
        return not_none(await asyncio.gather(*tasks))

    async def fuzz_parameter(self, session: aiohttp.ClientSession, args, method, path, params, param, payload):
        try:
            params_kwargs = {"params": params} if method == "get" else {"data": params}

            async with session.request(method, urljoin(args.url, path), **params_kwargs) as response:
                if response.status >= 500:
                    return {"type": "ERROR", "status": response.status, "method": method, "path": path, "param": param, "payload": payload}
        except:
            pass

    async def omit_parameters(self, session: aiohttp.ClientSession, args, dirs):
        tasks = []
        for directory, values in dirs.items():
            if "post-parameters" in values:
                param_names = values["post-parameters"].keys()
                for combination in itertools.combinations(param_names, len(param_names) - 1):
                    omit = (param_names - combination).pop()
                    params = {name: values["post-parameters"][name] for name in combination}
                    tasks.append(self.check_parameter_combination(session, args, "post", directory, params, omit))
            if "url-parameters" in values:
                param_names = values["url-parameters"].keys()
                for combination in itertools.combinations(param_names, len(param_names) - 1):
                    omit = (param_names - combination).pop()
                    params = {name: values["url-parameters"][name] for name in combination}
                    tasks.append(self.check_parameter_combination(session, args, "get", directory, params, omit))

        return not_none(await asyncio.gather(*tasks))

    async def check_parameter_combination(self, session: aiohttp.ClientSession, args, method, path, params, omit):
        try:
            params_kwargs = {"params": params} if method == "get" else {"data": params}

            async with session.request(method, urljoin(args.url, path), **params_kwargs) as response:
                if response.status >= 500:
                    return {"type": "Omit-Parameter", "status": response.status, "method": method, "path": path, "payload": omit}
        except:
            pass
