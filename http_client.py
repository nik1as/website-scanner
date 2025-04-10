import asyncio
import random
from abc import abstractmethod

from aiohttp import ClientSession, ClientResponse, ClientResponseError, ClientError, ServerDisconnectedError
from aiolimiter import AsyncLimiter


class RetryOptions:

    def __init__(self, attempts: int = 3):
        self.attempts = attempts

    @abstractmethod
    def get_timeout(self, attempt: int) -> float:
        raise NotImplementedError


class ExponentialRetry(RetryOptions):

    def __init__(self,
                 attempts: int = 3,
                 factor: float = 2.0):
        super().__init__(attempts)
        self.factor = factor

    def get_timeout(self, attempt: int) -> float:
        return self.factor ** attempt


class RandomRetry(RetryOptions):

    def __init__(self,
                 attempts: int = 3,
                 min_timeout: float = 1.0,
                 max_timeout: float = 5.0):
        super().__init__(attempts)
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout

    def get_timeout(self, attempt: int) -> float:
        return random.uniform(self.min_timeout, self.max_timeout)


class HTTPClient:

    def __init__(self,
                 client_session: ClientSession | None = None,
                 retry_options: RetryOptions | None = None,
                 rate_limit: int | None = None,
                 *args,
                 **kwargs):
        self.session = client_session or ClientSession(*args, **kwargs)
        self.retry_options = retry_options or ExponentialRetry()
        if rate_limit is None:
            self.limiter = None
        else:
            self.limiter = AsyncLimiter(rate_limit, 1)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def request(self, method: str, url: str, **kwargs):
        return Request(self, method, url, **kwargs)

    async def _request(self, method: str, url: str, **kwargs) -> ClientResponse:
        last_exception = None
        for attempt in range(self.retry_options.attempts + 1):
            try:
                if self.limiter is None:
                    return await self.session.request(method, url, **kwargs)
                else:
                    async with self.limiter:
                        return await self.session.request(method, url, **kwargs)
            except (ClientError, ClientResponseError, ServerDisconnectedError, asyncio.TimeoutError) as e:
                last_exception = e
                await asyncio.sleep(self.retry_options.get_timeout(attempt))

        raise last_exception

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.request("DELETE", url, **kwargs)


class Request:
    def __init__(self, client: HTTPClient, method: str, url: str, **kwargs):
        self.client = client
        self.method = method
        self.url = url
        self.kwargs = kwargs
        self.response = None

    async def __aenter__(self):
        self.response = await self.client._request(self.method, self.url, **self.kwargs)
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.response.close()
