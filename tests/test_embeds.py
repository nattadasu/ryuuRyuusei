import os
import sys
import unittest
from datetime import datetime, timezone
from unittest import mock

try:
    from classes.anilist import (
        AniListImageStruct,
        AniListMediaStruct,
        AniListTrailerStruct,
    )
    from classes.excepts import ProviderHttpError
    from classes.jikan import (
        JikanAnimeStruct,
        JikanBroadcastStruct,
        JikanDateStruct,
    )
    from classes.rawg import RawgGameData
    from modules.anilist import generate_anilist
    from modules.myanimelist import generate_mal
    from modules.nekomimidb import determine_domain
    from modules.rawg import generate_rawg
    from modules.simkl import create_simkl_embed
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.anilist import (
        AniListImageStruct,
        AniListMediaStruct,
        AniListTrailerStruct,
    )
    from classes.excepts import ProviderHttpError
    from classes.jikan import (
        JikanAnimeStruct,
        JikanBroadcastStruct,
        JikanDateStruct,
    )
    from classes.rawg import RawgGameData
    from modules.anilist import generate_anilist
    from modules.myanimelist import generate_mal
    from modules.nekomimidb import determine_domain
    from modules.rawg import generate_rawg
    from modules.simkl import create_simkl_embed


def _check_limits(testcase, embed):
    data = embed.to_dict()
    if data.get("description"):
        testcase.assertLessEqual(len(data["description"]), 4096)
    for field in data.get("fields", []):
        testcase.assertLessEqual(len(str(field.get("value", ""))), 1024)
        testcase.assertNotEqual(str(field.get("value", "")), "None")


def _simkl_base(**overrides):
    data = {"ids": {"simkl": 1}, "title": "Test Title"}
    data.update(overrides)
    return data


def _jikan_base(**overrides):
    data = {
        "mal_id": 999999,
        "url": "https://myanimelist.net/anime/999999",
        "images": None,
        "trailer": None,
        "approved": True,
        "titles": None,
        "title": "Test Anime",
        "title_english": None,
        "title_japanese": None,
        "type": "TV",
        "source": None,
        "episodes": None,
        "status": "Not yet aired",
        "airing": False,
        "aired": None,
        "duration": None,
        "rating": None,
        "score": None,
        "scored_by": None,
        "rank": None,
        "popularity": None,
        "members": None,
        "favorites": None,
        "synopsis": None,
        "background": None,
        "season": None,
        "year": None,
        "broadcast": None,
        "producers": None,
        "licensors": None,
        "studios": None,
        "genres": None,
        "explicit_genres": None,
        "themes": None,
        "demographics": None,
    }
    data.update(overrides)
    return JikanAnimeStruct(**data)


class SimklEmbedTest(unittest.IsolatedAsyncioTestCase):
    """SIMKL embed regression tests (offline)"""

    async def test_minimal_movie(self):
        """Test minimal payload renders within limits"""
        embed, buttons = await create_simkl_embed(
            _simkl_base(), "movies", is_channel_nsfw=True, is_media_nsfw=False
        )
        _check_limits(self, embed)
        self.assertEqual(buttons, [])

    async def test_many_genres(self):
        """Test more than 20 genres does not crash"""
        embed, _ = await create_simkl_embed(
            _simkl_base(genres=[f"Genre{i}" for i in range(21)]),
            "movies",
            is_channel_nsfw=True,
            is_media_nsfw=False,
        )
        _check_limits(self, embed)
        genres = next(
            f["value"] for f in embed.to_dict()["fields"] if f["name"] == "Genres"
        )
        self.assertIn("and 1 more", genres)

    async def test_missing_ids(self):
        """Test missing IDs raise a handled provider error"""
        with self.assertRaises(ProviderHttpError):
            await create_simkl_embed(
                {"title": "No IDs"},
                "movies",
                is_channel_nsfw=True,
                is_media_nsfw=False,
            )

    async def test_trailer_without_youtube(self):
        """Test trailer entries without youtube key are skipped"""
        embed, buttons = await create_simkl_embed(
            _simkl_base(trailers=[{"name": "Teaser"}]),
            "movies",
            is_channel_nsfw=True,
            is_media_nsfw=False,
        )
        _check_limits(self, embed)
        self.assertEqual(buttons, [])

    async def test_long_overview(self):
        """Test long multi-paragraph overview stays within limits"""
        overview = "Short hook.\n" + "\n".join(
            f"Paragraph {i} " + "lorem ipsum dolor sit amet " * 40 for i in range(8)
        )
        embed, _ = await create_simkl_embed(
            _simkl_base(overview=overview),
            "movies",
            is_channel_nsfw=True,
            is_media_nsfw=False,
        )
        _check_limits(self, embed)


class RawgEmbedTest(unittest.IsolatedAsyncioTestCase):
    """RAWG embed regression tests (offline)"""

    async def test_tba_game(self):
        """Test unreleased game without date renders"""
        embed, _ = await generate_rawg(
            RawgGameData(id=1, slug="tba", name="TBA Game", tba=True)
        )
        _check_limits(self, embed)

    async def test_minimal_game(self):
        """Test game with null collections renders"""
        embed, buttons = await generate_rawg(
            RawgGameData(id=1, slug="minimal", name="Minimal")
        )
        _check_limits(self, embed)
        self.assertEqual(buttons, [])

    async def test_none_native_title(self):
        """Test null native title does not render as None"""
        embed, _ = await generate_rawg(
            RawgGameData(id=1, slug="x", name="X", name_original=None)
        )
        native = next(
            f["value"] for f in embed.to_dict()["fields"] if f["name"] == "Native Title"
        )
        self.assertEqual(native, "*None*")


class MalNullShapeTest(unittest.IsolatedAsyncioTestCase):
    """MAL embed null-shape regression tests (offline, mocked fetch)"""

    async def _render(self, struct):
        with mock.patch(
            "classes.jikan.JikanApi.get_anime_data",
            new=mock.AsyncMock(return_value=struct),
        ):
            embed, _ = await generate_mal(999999, is_nsfw=True)
        _check_limits(self, embed)
        return embed

    async def test_all_null(self):
        """Test fully null payload renders"""
        await self._render(_jikan_base())

    async def test_broadcast_no_timezone(self):
        """Test broadcast without timezone falls back to date math"""
        struct = _jikan_base(
            status="Currently Airing",
            aired=JikanDateStruct(
                from_=datetime(2026, 1, 5, tzinfo=timezone.utc),
                to=None,
                prop=None,
                string="Jan 5, 2026 to ?",
            ),
            broadcast=JikanBroadcastStruct(
                day="Mondays", string="Mondays at 00:00", time="00:00", timezone=None
            ),
        )
        await self._render(struct)

    async def test_aired_string_null(self):
        """Test null aired string renders"""
        struct = _jikan_base(
            status="Currently Airing",
            aired=JikanDateStruct(
                from_=datetime(2026, 1, 5, tzinfo=timezone.utc),
                to=None,
                prop=None,
                string=None,
            ),
        )
        await self._render(struct)

    async def test_unrecognized_aired_string(self):
        """Test unrecognized aired string falls back to ISO date"""
        struct = _jikan_base(
            status="Currently Airing",
            aired=JikanDateStruct(
                from_=datetime(2027, 5, 1, tzinfo=timezone.utc),
                to=None,
                prop=None,
                string="Coming soon!!",
            ),
        )
        embed = await self._render(struct)
        aired = next(
            f["value"] for f in embed.to_dict()["fields"] if f["name"] == "Aired"
        )
        self.assertIn("2027-05-01", aired)


class AnilistEmbedTest(unittest.IsolatedAsyncioTestCase):
    """AniList embed regression tests (offline, mocked fetch)"""

    async def _render(self, media):
        with (
            mock.patch(
                "classes.anilist.AniList.manga",
                new=mock.AsyncMock(return_value=media),
            ),
            mock.patch(
                "classes.anilist.get_valid_access_token",
                new=mock.AsyncMock(return_value=None),
            ),
        ):
            result = await generate_anilist(1, is_nsfw=True)
        _check_limits(self, result[0])
        return result

    async def test_bad_color(self):
        """Test malformed cover color falls back to default"""
        media = AniListMediaStruct(
            id=1,
            coverImage=AniListImageStruct(
                extraLarge="https://example.com/x.jpg", color="notacolor"
            ),
        )
        await self._render(media)

    async def test_trailer_without_id(self):
        """Test youtube trailer without ID is skipped"""
        media = AniListMediaStruct(
            id=1, trailer=AniListTrailerStruct(id=None, site="youtube")
        )
        _, buttons = await self._render(media)
        self.assertEqual(buttons, [])

    def test_drop_null_tags(self):
        """Test nameless tags are dropped from raw payloads"""
        from classes.anilist import AniList

        payload = {
            "tags": [
                {"id": 1, "name": None, "isMediaSpoiler": False, "isAdult": False},
                {"id": 2, "name": "Action", "isMediaSpoiler": False, "isAdult": False},
            ]
        }
        AniList._drop_null_tags(payload)
        self.assertEqual([t["name"] for t in payload["tags"]], ["Action"])


class NekomimiTest(unittest.TestCase):
    """Nekomimi helper regression tests (offline)"""

    def test_malformed_url(self):
        """Test malformed image source URL does not crash"""
        self.assertEqual(determine_domain("not a url"), "Unknown")
        self.assertEqual(determine_domain(""), "Unknown")


if __name__ == "__main__":
    unittest.main(verbosity=2)
