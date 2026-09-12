import os
import sys
import unittest

try:
    from classes.jikan import JikanApi, JikanUserStruct
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.jikan import JikanApi, JikanUserStruct


class JikanTest(unittest.IsolatedAsyncioTestCase):
    """Jikan API test class"""

    async def test_get_anime_data(self):
        """Test getting anime data"""
        async with JikanApi() as jikan:
            anime = await jikan.get_anime_data(1)
            self.assertIsNotNone(anime)

    async def test_get_user_data(self):
        """Test getting user data"""
        async with JikanApi() as jikan:
            user = await jikan.get_user_data("nattadasu")
            self.assertIsNotNone(user)

    async def test_get_user_clubs(self):
        """Test getting user clubs"""
        async with JikanApi() as jikan:
            clubs = await jikan.get_user_clubs("nattadasu")
            self.assertIsNotNone(clubs)


class JikanConverterTest(unittest.TestCase):
    """Jikan converter tests (offline, no network)"""

    @staticmethod
    def _anime_base(**overrides):
        data = {
            "mal_id": 1,
            "url": "https://myanimelist.net/anime/1",
            "images": None,
            "trailer": None,
            "approved": True,
            "titles": None,
            "title": "Cowboy Bebop",
            "type": "TV",
            "source": None,
            "episodes": None,
            "status": None,
            "airing": None,
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
        return data

    def test_anime_minimal(self):
        """Test sparse anime payload with unknown keys does not crash"""
        data = self._anime_base(
            future_key="ignored",
            genres=[
                {"mal_id": 1, "type": "genre", "name": "Action"},
                "junk-entry",
                None,
                {"type": "genre"},
            ],
        )
        anime = JikanApi.anime_dict_to_dataclass(data)
        self.assertEqual(anime.mal_id, 1)
        self.assertIsNone(anime.images)
        self.assertIsNone(anime.aired)
        self.assertIsNotNone(anime.genres)
        self.assertNotIn("future_key", anime.__dict__)

    def test_anime_no_mutation(self):
        """Test conversion does not mutate the input payload"""
        data = self._anime_base(
            aired={
                "from": "1998-04-03T00:00:00+00:00",
                "to": None,
                "prop": {
                    "from": {"day": 3, "month": 4, "year": 1998},
                    "to": {"day": None, "month": None, "year": None},
                },
                "string": "Apr 3, 1998 to Apr 24, 1999",
            },
        )
        snapshot = dict(data)
        anime = JikanApi.anime_dict_to_dataclass(data)
        self.assertEqual(data, snapshot)
        self.assertIsNotNone(anime.aired)
        self.assertIsNotNone(anime.aired.prop)

    def test_anime_partial_aired(self):
        """Test aired block missing prop/from keys does not crash"""
        data = self._anime_base(
            title="TBA",
            aired={"string": "Not available"},
            broadcast={"string": "Unknown"},
        )
        anime = JikanApi.anime_dict_to_dataclass(data)
        self.assertIsNone(anime.aired.from_)
        self.assertIsNotNone(anime.broadcast)

    def test_parse_dt_variants(self):
        """Test datetime parsing tolerates format variance"""
        self.assertIsNotNone(JikanApi._parse_dt("1998-04-03T00:00:00+00:00"))
        self.assertIsNotNone(JikanApi._parse_dt("1998-04-03T00:00:00.000Z"))
        self.assertIsNone(JikanApi._parse_dt(None))
        self.assertIsNone(JikanApi._parse_dt(""))
        self.assertIsNone(JikanApi._parse_dt("not a date"))
        self.assertIsNone(JikanApi._parse_dt(12345))

    def test_user_minimal(self):
        """Test sparse user payload does not crash"""
        data = {
            "mal_id": 1,
            "username": "someone",
            "url": "https://myanimelist.net/profile/someone",
            "future_key": "ignored",
        }
        user = JikanApi.user_dict_to_dataclass(data)
        self.assertIsInstance(user, JikanUserStruct)
        self.assertEqual(user.username, "someone")
        self.assertIsNone(user.images)
        self.assertIsNone(user.statistics)

    def test_user_no_mutation(self):
        """Test user conversion does not mutate the input payload"""
        data = {
            "mal_id": 1,
            "username": "someone",
            "url": "https://myanimelist.net/profile/someone",
            "joined": "2020-01-01T00:00:00+00:00",
            "favorites": {
                "anime": [
                    {
                        "mal_id": 1,
                        "url": "https://myanimelist.net/anime/1",
                        "images": {
                            "jpg": {"image_url": "https://example.com/x.jpg"},
                        },
                        "title": "Cowboy Bebop",
                    }
                ]
            },
        }
        snapshot = {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in data.items()
        }
        user = JikanApi.user_dict_to_dataclass(data)
        self.assertEqual(data, snapshot)
        self.assertIsNotNone(user.favorites)
        assert user.favorites is not None
        self.assertIsNotNone(user.favorites.anime)


if __name__ == "__main__":
    unittest.main(verbosity=2)
