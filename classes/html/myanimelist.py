"""
# MyAnimeList HTML Scraper

This is a HTML scraper for MyAnimeList.
ONLY USE THIS IF YOU DO NOT WANT JIKAN AUTOCACHE
Can be easily broken if MAL changes their HTML structure
"""

import re
from datetime import datetime, timedelta, timezone

import aiohttp
from bs4 import BeautifulSoup

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
        await self.session.close()

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
        async with self.session.get(self.base_url + f"profile/{username}") as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.reason, resp.status)
            html = await resp.text()
        soup = BeautifulSoup(html, "html5lib")
        report_link = soup.find(
            "a", {"class": "header-right mt4 mr0"}).get("href")
        user_id = re.search(r"id=(\d+)", report_link).group(1)
        image_div = soup.find("div", class_="user-image mb8")
        if image_div:
            image = image_div.find("img")
            if image:
                image = image.get("data-src")
            else:
                image = None
        else:
            image = None

        # Extract the relevant information
        last_online = soup.find(
            "span",
            class_="user-status-title",
            text="Last Online")
        if last_online:
            last_online = last_online.find_next(
                "span", class_="user-status-data"
            ).text.strip()
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
                    case "Yesterday":
                        yesterday_str = (
                            datetime.now(timezone.utc) - timedelta(days=1)
                        ).strftime("%b %d, %Y")
                        last_online = datetime.strptime(
                            f"{yesterday_str} {activity[1]}", date_format
                        )
                    case _:
                        if len(activity) == 2:
                            # check if in activity[1] has a year after the comma
                            date_split = activity[1].split(" ")
                            if len(date_split[0]) == 4:
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
                            time_value: int = int(matching.group(1))
                            # get unit
                            time_unit: str = matching.group(2)
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

        gender = soup.find("span", class_="user-status-title", text="Gender")
        if gender:
            gender = gender.find_next(
                "span", class_="user-status-data").text.strip()
        else:
            gender = None

        birthday = soup.find(
            "span",
            class_="user-status-title",
            text="Birthday")
        if birthday:
            birthday = birthday.find_next(
                "span", class_="user-status-data"
            ).text.strip()
            try:
                birthday = datetime.strptime(birthday, "%b %d, %Y").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                birthday = None
        else:
            birthday = None

        location = soup.find(
            "span",
            class_="user-status-title",
            text="Location")
        if location:
            location = location.find_next(
                "span", class_="user-status-data"
            ).text.strip()
        else:
            location = None

        joined = soup.find("span", class_="user-status-title", text="Joined")
        if joined:
            joined = joined.find_next(
                "span", class_="user-status-data").text.strip()
            joined = datetime.strptime(
                joined, "%b %d, %Y").replace(
                tzinfo=timezone.utc)
        else:
            joined = None

        user = JikanUserStruct(
            mal_id=int(user_id),
            username=username,
            url=self.base_url + f"profile/{username}",
            images=JikanImages(
                jpg=JikanImageStruct(image_url=image),
                webp=JikanImageStruct(image_url=image),
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
