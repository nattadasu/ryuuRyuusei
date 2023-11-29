"""# Urban Dictionary Unofficial API Wrapper"""

import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote

import aiohttp
from interactions import Embed
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent

from classes.excepts import ProviderHttpError


USER_AGENT = FakeUserAgent().random


@dataclass
class UrbanDictionaryEntry:
    """Dataclass of Urban Dictionary entry"""

    definition: str
    """Definition of the word"""
    permalink: str
    """Permalink of the word"""
    thumbs_up: int
    """Number of thumbs up"""
    author: str
    """Word definition author"""
    word: str
    """Keyword"""
    defid: int
    """Definition ID"""
    current_vote: str
    """Current vote"""
    written_on: datetime
    """Date written on"""
    example: str
    """Example of the word"""
    thumbs_down: int
    """Number of thumbs down"""

    @property
    def embed(self) -> Embed:
        """
        Get embed of the word

        Returns:
            Embed: Embed of the word
        """
        embed = Embed(
            title=self.word,
            url=self.permalink,
            description=f"{self.definition}",
            color=0x1b2936,
        )
        embed.add_field(
            name="Example",
            value=self.example,
            inline=False,
        )
        embed.add_field(
            name="Author",
            value=self.author,
            inline=True,
        )
        embed.set_author(
            name="Urban Dictionary",
            url="https://www.urbandictionary.com/",
        )
        # percentage of thumbs up
        percentage = round(
            (self.thumbs_up / (self.thumbs_up + self.thumbs_down)) * 100
        )
        embed.set_footer(
            text=f"👍 {self.thumbs_up} / {self.thumbs_down} ({percentage}%)"
        )
        embed.timestamp = self.written_on  # type: ignore
        return embed


class UrbanDictionary:
    """Urban Dictionary Unofficial API Wrapper"""

    def __init__(self):
        """Initialize Urban Dictionary API Wrapper"""
        self.session = None
        self.header = None
        self.base_url = "https://api.urbandictionary.com/v0"

    async def __aenter__(self):
        """Async enter"""
        self.session = aiohttp.ClientSession()
        self.header = {"User-Agent": USER_AGENT}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        """Async exit"""
        await self.close()

    async def close(self):
        """Close session"""
        await self.session.close() if self.session else None

    @staticmethod
    def _add_hyperlinks(text: str) -> str:
        """
        Add hyperlinks to text if Urban Dictionary has wiki markup

        Args:
            text (str): Text to check

        Returns:
            str: Replaced text
        """
        ud_link_pattern = re.compile(r'\[([^\]]+)\]')

        # Find all matches in the text
        matches = ud_link_pattern.findall(text)

        # Replace each Urban Dictionary hyperlink with Markdown format
        for match in matches:
            urban_dictionary_link = f'https://www.urbandictionary.com/define.php?term={quote(match)}'
            markdown_link = f'[{match}]({urban_dictionary_link})'
            text = text.replace(f'[{match}]', markdown_link)

        return text

    async def lookup_definition(self, term: str) -> list[UrbanDictionaryEntry]:
        """
        Lookup definition of a word

        Args:
            term (str): Term to lookup

        Returns:
            list[UrbanDictionaryEntry]: List of UrbanDictionaryEntry
        """
        if self.session is None:
            raise Exception("Urban Dictionary session not initialized")
        params = {"term": term}
        async with self.session.get(
            f"{self.base_url}/define", headers=self.header, params=params
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    f"Urban Dictionary unable to lookup definition of {term}",
                    resp.status,
                )
            data = await resp.json()
            if len(data["list"]) == 0:
                raise ProviderHttpError(
                    f"{term} not found in Urban Dictionary", 404)
            listed: list[UrbanDictionaryEntry] = []
            for entry in data["list"]:
                # convert wiki markup to markdown
                entry["definition"] = self._add_hyperlinks(entry["definition"])
                entry["example"] = self._add_hyperlinks(entry["example"])
                entry["written_on"].replace("Z", "+00:00")
                entry["written_on"] = datetime.fromisoformat(
                    entry["written_on"])
                listed += [UrbanDictionaryEntry(**entry)]

            return listed

    async def _fetch_raw_html(self, path: str = "") -> str:
        """
        Fetch raw HTML of Urban Dictionary

        Args:
            path (str, optional): Path to fetch. Defaults to "".

        Returns:
            str: Raw HTML of Urban Dictionary
        """
        if self.session is None:
            raise Exception("Urban Dictionary session not initialized")
        async with self.session.get(
            f"https://www.urbandictionary.com/{path}", headers=self.header
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    "Urban Dictionary unable to fetch raw HTML", resp.status
                )
            return await resp.text()

    async def _parse_html(self, html: str) -> UrbanDictionaryEntry:
        """
        Parse HTML

        Args:
            html (str): HTML to parse

        Returns:
            BeautifulSoup: Parsed HTML
        """
        soup = BeautifulSoup(html, "html5lib")
        word_element = soup.find("h1", class_="flex-1")
        if word_element:
            word = word_element.text.strip()
            definition = await self.lookup_definition(word)
            return definition[0]
        raise ProviderHttpError(
            "Urban Dictionary unable to fetch word of the day", 404)

    async def get_word_of_the_day(self) -> UrbanDictionaryEntry:
        """
        Get word of the day

        Returns:
            UrbanDictionaryEntry: Word of the day
        """
        html = await self._fetch_raw_html()
        return await self._parse_html(html)

    async def get_random_word(self) -> list[UrbanDictionaryEntry]:
        """
        Get random word

        Returns:
            list[UrbanDictionaryEntry]: Random word
        """
        if self.session is None:
            raise Exception("Urban Dictionary session not initialized")
        async with self.session.get(
            f"{self.base_url}/random", headers=self.header
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(
                    "Urban Dictionary unable to get random definition",
                    resp.status,
                )
            data = await resp.json()
            listed: list[UrbanDictionaryEntry] = []
            for entry in data["list"]:
                # convert wiki markup to markdown
                entry["definition"] = self._add_hyperlinks(entry["definition"])
                entry["example"] = self._add_hyperlinks(entry["example"])
                entry["written_on"].replace("Z", "+00:00")
                entry["written_on"] = datetime.fromisoformat(
                    entry["written_on"])
                listed += [UrbanDictionaryEntry(**entry)]

            return listed
