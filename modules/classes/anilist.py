"""AniList Asynchronous API Wrapper"""

import aiohttp

from modules.classes.excepts import AniListHttpError, AniListTypeError

class AniList:
    """AniList Asynchronous API Wrapper"""

    def __init__(self):
        self.base_url = "https://graphql.anilist.co"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    async def nsfwCheck(self, media_id: int, media_type: str = "ANIME"):
        """Check if the media is NSFW"""
        if media_type == "ANIME":
            query = f"""query {{
    Media(id: {media_id}, type: ANIME) {{
        id
        isAdult
    }}
}}"""
        elif media_type == "MANGA":
            query = f"""query {{
    Media(id: {media_id}, type: MANGA) {{
        id
        isAdult
    }}
}}"""
        else:
            raise AniListTypeError("Media type must be either ANIME or MANGA")
        async with self.session.post(self.base_url, json={"query": query}) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]["Media"]["isAdult"]
            else:
                error_message = await response.text()
                raise AniListHttpError(error_message, response.status)

    async def manga(self, media_id: int):
        """Get manga information by its ID"""
        gqlquery = f"""query {{
    Media(id: {media_id}, type: MANGA) {{
        id
        idMal
        title {{
            romaji
            english
            native
        }}
        isAdult
        description(asHtml: false)
        synonyms
        format
        startDate {{
            year
            month
            day
        }}
        endDate {{
            year
            month
            day
        }}
        status
        chapters
        volumes
        coverImage {{
            extraLarge
            large
        }}
        bannerImage
        genres
        tags {{
            name
            isMediaSpoiler
        }}
        averageScore
        stats {{
            scoreDistribution {{
                score
                amount
            }}
        }}
        trailer {{
            id
            site
        }}
    }}
}}"""
        async with self.session.post(self.base_url, json={"query": gqlquery}) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]["Media"]
            else:
                error_message = await response.text()
                raise AniListHttpError(error_message, response.status)

    async def search(self, query: str, limit: int = 10, media_type: str = "MANGA"):
        """Search anime by its title"""
        if limit > 10:
            raise AniListTypeError("limit must be less than or equal to 10", "int")
        gqlquery = f"""query ($search: String, $mediaType: MediaType, $limit: Int) {{
    Page(page: 1, perPage: $limit) {{
        results: media(search: $search, type: $mediaType) {{
            id
            title {{
                romaji
                english
                native
            }}
            format
            isAdult
            startDate {{
                year
            }}
        }}
    }}
}}"""
        variables = {
            "search": query,
            "mediaType": media_type,
            "limit": limit,
        }
        async with self.session.post(self.base_url, json={"query": gqlquery, "variables": variables}) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]["Page"]["results"]
            else:
                error_message = await response.text()
                raise AniListHttpError(error_message, response.status)


__all__ = ["AniList"]
