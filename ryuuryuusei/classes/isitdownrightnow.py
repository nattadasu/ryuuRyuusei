import re
from dataclasses import dataclass
from typing import Optional

import aiohttp
import validators
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent as UserAgent


@dataclass
class WebsiteStatus:
    """A dataclass to represent the status of a website."""

    website_name: str
    """The name of the website."""
    url_checked: str
    """The URL of the website."""
    response_time: str
    """The response time of the website."""
    last_down: Optional[str]
    """The last time the website was down."""
    status_message: Optional[str]
    """The status message of the website."""


class WebsiteChecker:
    """A class to check the status of a websit using isitdownrightnow.com."""

    def __init__(self):
        """Initialize the WebsiteChecker class."""
        self.err_msg: str = ""
        self.headers: dict = {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Enter the async context manager."""
        self.headers: dict = {"User-Agent": self._get_random_user_agent()}
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the async context manager."""
        await self.close()

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()

    @staticmethod
    def _get_random_user_agent() -> str:
        """
        Get a random user agent.

        Returns:
            str: A random user agent.
        """
        ua = UserAgent(browsers=["chrome", "firefox", "edge"])
        return ua.random

    async def check_website(self, url: str) -> Optional[WebsiteStatus]:
        """
        Check the status of a website.

        Args:
            url (str): The URL of the website to check.

        Raises:
            Exception: If the HTTP status code is not 200.
            validators.ValidationFailure: If the URL is not valid.

        Returns:
            Optional[WebsiteStatus]: The status of the website if successful, None otherwise.
        """
        if re.match(r"^https?://", url) is None:
            url = "https://" + url
        validators.url(url)
        if url.startswith("http://") or url.startswith("https://"):
            url = url.split("//")[1]
        if url.startswith("www."):
            url = re.sub(r"^www.", "", url)

        params = {"domain": url}
        async with self.session.get(
            "https://www.isitdownrightnow.com/check.php", params=params
        ) as resp:
            if resp.status != 200:
                raise Exception(f"HTTP error {resp.status}: {resp.reason}")

            html_response = await resp.text()

            soup = BeautifulSoup(html_response, "html5lib")

            div_elements = soup.find_all(
                "div", class_=lambda x: x in ["tabletr", "tabletrsimple"]
            )

            website_name = div_elements[0].span.text.strip()
            url_checked = div_elements[1].span.text.strip()
            response_time = div_elements[2].span.text.strip()
            last_down_str = div_elements[3].span.text.strip()
            status_message = div_elements[4].span.text.strip()

            status = WebsiteStatus(
                website_name=website_name,
                url_checked=url_checked,
                response_time=response_time,
                last_down=last_down_str,
                status_message=status_message,
            )

        return status
