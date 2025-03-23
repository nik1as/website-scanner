import os
from abc import ABC, abstractmethod

import aiohttp

from utils import load_modules


class VulnerabilityModule(ABC):
    modules = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.modules.append(cls)

    @abstractmethod
    async def run(self, session: aiohttp.ClientSession, args, dirs):
        pass

    def get_requests(self, dirs, payloads):
        for payload in payloads:
            for directory, values in dirs.items():
                if "post-parameters" in values:
                    param_names = values["post-parameters"].keys()
                    for param in param_names:
                        params = {name: "" for name in param_names}
                        params[param] = payload
                        yield "post", directory, params, param, payload
                if "url-parameters" in values:
                    param_names = values["url-parameters"].keys()
                    for param in param_names:
                        params = {name: "" for name in param_names}
                        params[param] = payload
                        yield "get", directory, params, param, payload


load_modules(os.path.abspath(__file__))
