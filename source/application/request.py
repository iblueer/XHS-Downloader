from typing import TYPE_CHECKING

from curl_cffi.requests import RequestsError

from ..module import ERROR, Manager, logging, retry, sleep_time
from ..translation import _

if TYPE_CHECKING:
    from ..module import Manager

__all__ = ["Html"]


class Html:
    def __init__(
        self,
        manager: "Manager",
    ):
        self.retry = manager.retry
        self.client = manager.request_client
        self.headers = manager.headers
        self.timeout = manager.timeout

    @retry
    async def request_url(
        self,
        url: str,
        content=True,
        log=None,
        cookie: str = None,
        proxy: str = None,
        **kwargs,
    ) -> str:
        if not url.startswith("http"):
            url = f"https://{url}"
        headers = self.update_cookie(
            cookie,
        )
        if ua := kwargs.pop("user_agent", None):
            headers = headers | {"User-Agent": ua}
        # print(f"DEBUG: kwargs keys after pop: {list(kwargs.keys())}")

        try:
            match bool(proxy):
                case False:
                    response = await self.__request_url_get(
                        url,
                        headers,
                        **kwargs,
                    )
                    await sleep_time()
                    response.raise_for_status()
                    return response.text if content else str(response.url)
                case True:
                    response = await self.__request_url_get_proxy(
                        url,
                        headers,
                        proxy,
                        **kwargs,
                    )
                    await sleep_time()
                    response.raise_for_status()
                    return response.text if content else str(response.url)
                case _:
                    raise ValueError
        except RequestsError as error:
            logging(
                log, _("网络异常，{0} 请求失败: {1}").format(url, repr(error)), ERROR
            )
            return ""

    @staticmethod
    def format_url(url: str) -> str:
        return bytes(url, "utf-8").decode("unicode_escape")

    def update_cookie(
        self,
        cookie: str = None,
    ) -> dict:
        return self.headers | {"Cookie": cookie} if cookie else self.headers.copy()

    async def __request_url_head(
        self,
        url: str,
        headers: dict,
        **kwargs,
    ):
        return await self.client.head(
            url,
            headers=headers,
            **kwargs,
        )

    async def __request_url_head_proxy(
        self,
        url: str,
        headers: dict,
        proxy: str,
        **kwargs,
    ):
        return await self.client.head(
            url,
            headers=headers,
            proxy=proxy,
            follow_redirects=True,
            verify=False,
            timeout=self.timeout,
            **kwargs,
        )

    async def __request_url_get(
        self,
        url: str,
        headers: dict,
        **kwargs,
    ):
        return await self.client.get(
            url,
            headers=headers,
            **kwargs,
        )

    async def __request_url_get_proxy(
        self,
        url: str,
        headers: dict,
        proxy: str,
        **kwargs,
    ):
        return await self.client.get(
            url,
            headers=headers,
            proxies={"http": proxy, "https": proxy},
            **kwargs,
        )
