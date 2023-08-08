"""
# MyAnimeList HTML Scraper

This is a HTML scraper for MyAnimeList.
ONLY USE THIS IF YOU DO NOT WANT JIKAN AUTOCACHE
Can be easily broken if MAL changes their HTML structure
"""

import re
from datetime import datetime, timedelta, timezone

import aiohttp
from bs4 import BeautifulSoup, Tag

from classes.excepts import ProviderHttpError
from classes.jikan import JikanImages, JikanImageStruct, JikanUserStruct
from modules.const import USER_AGENT


class HtmlMyAnimeList:
    """MyAnimeList HTML Scraper"""

    def __init__(self, user_agent: str = USER_AGENT):
        """Initialize the class"""
        self.user_agent = user_agent
        self.base_url = "https://myanimelist.net/"
        self.headers = {}
        self.session = None

    async def __aenter__(self):
        """Create a new session"""
        self.headers["User-Agent"] = self.user_agent
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Close the session"""
        await self.close()

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
        return

    async def get_user(self, username: str) -> JikanUserStruct:
        """
        Get user information, realtime

        Args:
            username (str): Username

        Raises:
            JikanException: User or Client error

        Returns:
            JikanUserStruct: User information
        """
        if not self.session:
            raise RuntimeError("Session not created")
        async with self.session.get(self.base_url + f"profile/{username}") as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.reason, resp.status)
            html = await resp.text()
        soup = BeautifulSoup(html, "html5lib")
        report_link = soup.find(
            "a", {"class": "header-right mt4 mr0"})
        if not isinstance(report_link, Tag):
            raise RuntimeError("Could not find user information")
        report_link = report_link.get("href")
        if not report_link:
            raise RuntimeError("Could not find user information")
        elif isinstance(report_link, list):
            report_link = report_link[0]
        user_id = re.search(r"id=(\d+)", report_link).group(1)  # type: ignore
        image_div = soup.find("div", class_="user-image mb8")
        if image_div:
            image = image_div.find("img")
            if isinstance(image, Tag):
                image = image.get("data-src")
            else:
                image = None
        else:
            image = None

        if isinstance(image, list):
            image = image[0]

        # Extract the relevant information
        last_online = soup.find(
            "span",
            class_="user-status-title",
            text="Last Online")
        if last_online:
            last_online = last_online.find_next(
                "span", class_="user-status-data"
            )
            if not last_online:
                raise RuntimeError("Could not find user information")
            last_online = last_online.text.strip()
            if last_online == "Now":
                last_online = datetime.now(timezone.utc)
            else:
                last_online += " -0700"
                activity = last_online.split(", ")
                date_format = "%b %d, %Y %H:%M %p %z"
                match activity[0]:
                    case "Today":
                        today_str = datetime.now(
                            timezone.utc).strftime("%b %d, %Y")
                        last_online = datetime.strptime(
                            f"{today_str} {activity[1]}", date_format
                        )
                        # last_online -= timedelta(days=1)
                    case "Yesterday":
                        yesterday_str = (
                            datetime.now(timezone.utc) - timedelta(days=1)
                        ).strftime("%b %d, %Y")
                        last_online = datetime.strptime(
                            f"{yesterday_str} {activity[1]}", date_format
                        )
                        # last_online -= timedelta(days=1)
                    case _:
                        if len(activity) == 2:
                            # check if in activity[1] has a year after the comma
                            date_split = activity[1].split(" ")
                            if re.match(r"\d{4}", date_split[0]) is not None:
                                last_online = datetime.strptime(
                                    f"{activity[0]}, {activity[1]}", date_format
                                )
                            else:
                                current_year = datetime.now(timezone.utc).year
                                last_online = datetime.strptime(
                                    f"{activity[0]}, {current_year} {activity[1]}",
                                    date_format
                                )
                        else:
                            # handle relative time like 1 hour ago
                            regex = r"(\d+) (\w+) ago"
                            matching = re.search(regex, activity[0])
                            # get time
                            time_value: int = int(matching.group(1))  # type: ignore
                            # get unit
                            time_unit: str = matching.group(2)  # type: ignore
                            # add s to the unit if it is not already there
                            if not time_unit.endswith("s"):
                                time_unit += "s"
                            # convert to timedelta
                            time_delta = timedelta(**{time_unit: time_value})
                            # get the current time
                            current_time = datetime.now(timezone.utc)
                            last_online = current_time - time_delta
        else:
            last_online = None

        gender: str | None = None
        gender_find = soup.find(
            "span",
            class_="user-status-title",
            text="Gender")
        if gender_find:
            gender_find = gender_find.find_next(
                "span", class_="user-status-data")
            if gender_find:
                gender = gender_find.text.strip()


        birthday: datetime | None = None
        birthday_find = soup.find(
            "span",
            class_="user-status-title",
            text="Birthday")
        if birthday_find:
            birthday_find = birthday_find.find_next(
                "span", class_="user-status-data"
            )
            if birthday_find:
                birthday_str = birthday_find.text.strip()
                try:
                    birthday = datetime.strptime(birthday_str, "%b %d, %Y").replace(
                        tzinfo=timezone.utc
                    )
                except ValueError:
                    birthday = None

        location = None
        location_find = soup.find(
            "span",
            class_="user-status-title",
            text="Location")
        if location_find:
            location_find = location_find.find_next(
                "span", class_="user-status-data"
            )
            if location_find:
                location = location_find.text.strip()

        joined = None
        joined_find = soup.find("span", class_="user-status-title", text="Joined")
        if joined_find:
            joined_find = joined_find.find_next(
                "span", class_="user-status-data")
            if joined_find:
                joined_find = joined_find.text.strip()
                joined = datetime.strptime(
                    joined_find, "%b %d, %Y").replace(
                    tzinfo=timezone.utc)

        user = JikanUserStruct(
            mal_id=int(user_id),
            username=username,
            url=self.base_url + f"profile/{username}",
            images=JikanImages(
                jpg=JikanImageStruct(image_url=image) if image else None,
                webp=JikanImageStruct(image_url=image) if image else None,
            ),
            last_online=last_online,
            birthday=birthday,
            gender=gender,
            location=location,
            joined=joined,
            about=None,
            statistics=None,
            favorites=None,
            external=None,
            updates=None,
        )

        return user
