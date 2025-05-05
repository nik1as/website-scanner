import os
from abc import ABC, abstractmethod

import aiohttp

from website_scanner.utils import load_modules, fill_param


class VulnerabilityModule(ABC):
    modules = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.modules.append(cls)

    @abstractmethod
    async def run(self, session: aiohttp.ClientSession, args, dirs):
        pass

    def get_requests(self, directories: dict, fill: bool = False):
        for directory, values in directories.items():
            if "post-parameters" in values:
                param_names = values["post-parameters"].keys()
                for param in param_names:
                    if fill:
                        params = {name: fill_param(name) for name in param_names}
                    else:
                        params = {name: "" for name in param_names}
                    yield "POST", directory, params, param
            if "url-parameters" in values:
                param_names = values["url-parameters"].keys()
                for param in param_names:
                    if fill:
                        params = {name: fill_param(name) for name in param_names}
                    else:
                        params = {name: "" for name in param_names}
                    yield "GET", directory, params, param


load_modules(os.path.abspath(__file__))
