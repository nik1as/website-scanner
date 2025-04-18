import os
from abc import ABC, abstractmethod

import aiohttp

from website_scanner.utils import load_modules


class Module(ABC):
    modules = []

    def __init__(self, name: str):
        self.name = name

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.modules.append(cls)

    async def start(self, session: aiohttp.ClientSession, args):
        return self.name, await self.run(session, args)

    @abstractmethod
    async def run(self, session: aiohttp.ClientSession, args):
        pass


load_modules(os.path.abspath(__file__))
