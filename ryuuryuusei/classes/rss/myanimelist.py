"""
MyAnimeList RSS Feed Parser

Parse MyAnimeList RSS Feed to show the latest updates of a user's anime/manga list.

Example:
    >>> from classes.rss.myanimelist import MyAnimeListRss
    >>> async def main():
    ...     async with MyAnimeListRss(media_type="anime") as rss:
    ...         feeds = await rss.get_user("username")
    ...         print(feeds)
    >>> asyncio.run(main())
    [
        RssItem(
            title="...",
            url="...",
            status="...",
            progress_from="...",
            progress_to="...",
            updated=datetime.datetime(...),
        ),
        ...
    ]
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal

import aiohttp
import defusedxml.ElementTree as ET
from fake_useragent import FakeUserAgent

from classes.excepts import ProviderHttpError

user_agent = FakeUserAgent(browsers=['chrome', 'firefox', "opera"]).random


class MediaStatus(Enum):
    """Media status enum"""

    WATCHING = "Watching"
    READING = "Reading"
    COMPLETED = "Completed"
    ON_HOLD = "On-Hold"
    DROPPED = "Dropped"
    PLAN_TO_WATCH = "Plan to Watch"
    PLAN_TO_READ = "Plan to Read"


@dataclass
class RssItem:
    """RSS Item"""

    title: str
    """str: The title of the media"""
    url: str
    """str: The url of the media"""
    status: MediaStatus
    """MediaStatus: The status of the media"""
    progress_from: int
    """int: The progress of the media"""
    progress_to: int | None
    """int | None: The total progress of the media"""
    updated: datetime
    """datetime: The last updated date of the media"""


class MyAnimeListRss:
    """MyAnimeList RSS Feed Parser"""

    def __init__(
            self,
            media_type: Literal["anime", "manga"] = "anime",
            fetch_individual: bool = False):
        """
        Initialize the class

        Args:
            media_type (Literal["anime", "manga"], optional): The type of media to parse. Defaults to "anime".
            fetch_individual (bool, optional): Whether to fetch individual media. Defaults to False.
        """
        if media_type == "anime" and fetch_individual:
            self.media_type = "rwe"
        elif media_type == "manga" and fetch_individual:
            self.media_type = "rrm"
        elif media_type == "anime" and not fetch_individual:
            self.media_type = "rw"
        elif media_type == "manga" and not fetch_individual:
            self.media_type = "rm"
        self.fetch_individual = fetch_individual
        self.user_agent = user_agent
        self.username: str | None = None
        self.feeds: str | None = None
        self.session = None

    async def __aenter__(self):
        """Create a new session"""
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": self.user_agent})
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Close the session"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close()

    def _parse_title(self, title: str) -> str:
        """Parse title from string to string"""
        token = title.split(" - ")
        if self.fetch_individual is False:
            # remove the last token
            token.pop()
        return " - ".join(token)

    @staticmethod
    def _parse_date(date: str) -> datetime:
        """Parse date from string to datetime object"""
        return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")

    @staticmethod
    def _parse_status(status: str) -> MediaStatus:
        """Parse status from string to MediaStatus enum"""
        match status:
            case "Watching":
                return MediaStatus.WATCHING
            case "Reading":
                return MediaStatus.READING
            case "Completed":
                return MediaStatus.COMPLETED
            case "On-Hold":
                return MediaStatus.ON_HOLD
            case "Dropped":
                return MediaStatus.DROPPED
            case "Plan to Watch":
                return MediaStatus.PLAN_TO_WATCH
            case "Plan to Read":
                return MediaStatus.PLAN_TO_READ
            case _:
                ...

    @staticmethod
    def _parse_progress(progress: str) -> tuple[int, int | None]:
        """Parse progress from string to tuple[int, int | None]"""
        progress = progress.split(" - ")[1].split(" of ")
        progress_from = int(progress[0]) if progress[0].isdigit() else 0
        progress[1] = progress[1].split(" ")[0]
        progress_to = int(progress[1]) if progress[1].isdigit() else None
        return (progress_from, progress_to)

    @staticmethod
    def _parse_url(url: str) -> str:
        """Parse url from string to string"""
        urls = url.split("/")
        return f"https://myanimelist.net/{urls[3]}/{urls[4]}"

    def _parse_xml(self, xml: str) -> list[RssItem]:
        """Parse xml from string to list[RssItem]"""
        root = ET.fromstring(xml)
        item: list[RssItem] = []
        for data in root.iter("item"):
            title = self._parse_title(data.find("title").text)
            url = self._parse_url(data.find("link").text)
            # get CDATA from description
            description = data.find("description").text
            status = self._parse_status(description.split(" - ")[0])
            progress_from, progress_to = self._parse_progress(description)
            updated = self._parse_date(data.find("pubDate").text)
            item.append(RssItem(title, url, status,
                        progress_from, progress_to, updated))

        return item

    async def get_user(self, username: str) -> list[RssItem]:
        """
        Get user's RSS feed

        Args:
            username (str): The username of the user

        Raises:
            ProviderHttpError: If the request failed

        Returns:
            list[RssItem]: The RSS feeds
        """
        self.username = username
        async with self.session.get(f"https://myanimelist.net/rss.php?type={self.media_type}&u={self.username}") as resp:
            if resp.status != 200:
                raise ProviderHttpError("Failed to get RSS feed", resp.status)
            xml = await resp.text()
            feeds = self._parse_xml(xml)

        return feeds
