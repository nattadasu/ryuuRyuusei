from dataclasses import dataclass
from enum import Enum
from typing import Any, Union

from interactions import EmbedField


class Platform(Enum):
    """Enum for all supported platforms.

    Attributes:
        ARTSTATION (str): ArtStation.
        DEVIANTART | DA (str): DeviantArt.
        DISCORD (str): Discord.
        FACEBOOK | FB (str): Facebook.
        FLICKR (str): Flickr.
        HOYOLAB | HOYO (str): Hoyoverse/miHoYo forums.
        INSTAGRAM | IG (str): Instagram.
        LOFTER (str): Lofter.
        NICONICOSEIGA | NICONICO | SEIGA | NNS (str): Niconico Seiga.
        PATREON (str): Patreon.
        PIXIV (str): Pixiv.
        REDDIT (str): Reddit.
        TUMBLR (str): Tumblr.
        TWITTER | TW (str): Twitter.
        WEIBO (str): Weibo.
        ALLCINEMA | ALLCIN (str): All Cinema.
        ANIDB (str): AniDB.
        ANILIST | AL (str): AniList.
        ANIMENEWSNETWORK | ANN (str): Anime News Network.
        ANIMEPLANET | AP (str): Anime-Planet.
        ANISEARCH | AS (str): AniSearch.
        ANNICT (str): Annict.
        IMDB (str): IMDb.
        KAIZE (str): Kaize.
        KITSU (str): Kitsu.
        LASTFM | LAST | LFM (str): Last.fm.
        LETTERBOXD | LB (str): Letterboxd.
        LIVECHART | LC (str): LiveChart.me.
        MYANIMELIST | MAL (str): MyAnimeList.
        NOTIFYMOE | NOTIFY (str): Notify.moe.
        OTAKOTAKU | OTAKU | OO (str): Otakotaku.
        SHIKIMORI | SHIKI (str): Shikimori.
        SHOBOI | SYOBOI (str): Syoboi Calendar.
        SILVERYASHA | DBTI | SY (str): SilverYasha DB Tontonan Indonesia.
        SIMKL (str): Simkl.
        THEMOVIEDATABASE | TMDB (str): The Movie Database.
        THETVDB | TVDB (str): TheTVDB.
        TRAKT (str): Trakt.tv.
        TVTIME (str): TV Time.
    """

    # SNS
    ARTSTATION = "artstation"
    DEVIANTART = DA = "deviantart"
    DISCORD = "discord"
    FACEBOOK = FB = "facebook"
    FLICKR = "flickr"
    HOYOLAB = HOYO = "hoyolab"
    IBISPAINT = "ibispaint"
    INSTAGRAM = IG = "instagram"
    LOFTER = "lofter"
    NICONICOSEIGA = NICONICO = SEIGA = NNS = "seiga"
    PATREON = "patreon"
    PIXIV = "pixiv"
    REDDIT = "reddit"
    TUMBLR = "tumblr"
    TWITTER = TW = "twitter"
    WEIBO = "weibo"
    # Media tracking
    ALLCINEMA = ALLCIN = "allcin"
    ANIDB = "anidb"
    ANILIST = AL = "anilist"
    ANIMENEWSNETWORK = ANN = "animenewsnetwork"
    ANIMEPLANET = AP = "animeplanet"
    ANISEARCH = AS = "anisearch"
    ANNICT = "annict"
    IMDB = "imdb"
    KAIZE = "kaize"
    KITSU = "kitsu"
    LASTFM = LAST = LFM = "lastfm"
    LETTERBOXD = LB = "letterboxd"
    LIVECHART = LC = "livechart"
    MYANIMELIST = MAL = "myanimelist"
    NAUTILJON = NJ = "nautiljon"
    NOTIFYMOE = NOTIFY = "notify"
    OTAKOTAKU = OTAKU = OO = "otakotaku"
    SHIKIMORI = SHIKI = "shikimori"
    SHOBOI = SYOBOI = "shoboi"
    SILVERYASHA = DBTI = SY = "silveryasha"
    SIMKL = "simkl"
    THEMOVIEDATABASE = TMDB = "tmdb"
    THETVDB = TVDB = "tvdb"
    TRAKT = "trakt"
    TVTIME = "tvtime"


@dataclass
class PlatformLink:
    """Object of the formatted ID of the platform"""

    pf: str
    """The name of the platform"""
    uid: str
    """The formatted ID of the platform, a link"""
    emoid: str
    """Discord Emoji snowflake ID"""


@dataclass
class PlatformConfig:
    """Configuration for a platform"""

    name: str
    """Display name of the platform"""
    color: int
    """Color code for the platform"""
    emoji_id: str
    """Discord emoji snowflake ID"""
    url_template: str
    """URL template with {media_id} or {simkl_type} placeholders"""


# Centralized platform configuration
PLATFORM_CONFIGS = {
    # SNS
    "artstation": PlatformConfig(
        "ArtStation", 0x0F0F0F, "0", "https://www.artstation.com/artwork/{media_id}"
    ),
    "deviantart": PlatformConfig(
        "DeviantArt", 0x05CC47, "0", "https://www.deviantart.com/{media_id}"
    ),
    "discord": PlatformConfig(
        "Discord", 0x7289DA, "0", "https://discord.com/users/{media_id}"
    ),
    "facebook": PlatformConfig(
        "Facebook", 0x3B5998, "0", "https://www.facebook.com/{media_id}"
    ),
    "flickr": PlatformConfig(
        "Flickr", 0xFF0084, "0", "https://www.flickr.com/photos/{media_id}"
    ),
    "hoyolab": PlatformConfig(
        "Hoyolab",
        0x1B75BB,
        "0",
        "https://www.hoyolab.com/accountCenter/postList?id={media_id}",
    ),
    "ibispaint": PlatformConfig(
        "ibisPaint", 0x1F507B, "0", "https://ibispaint.com/art/{media_id}"
    ),
    "instagram": PlatformConfig(
        "Instagram", 0x833AB4, "0", "https://www.instagram.com/{media_id}"
    ),
    "lofter": PlatformConfig("Lofter", 0x335F60, "0", "https://{media_id}.lofter.com"),
    "patreon": PlatformConfig(
        "Patreon", 0xF96854, "0", "https://www.patreon.com/{media_id}"
    ),
    "pixiv": PlatformConfig(
        "Pixiv", 0x0096FA, "0", "https://www.pixiv.net/users/{media_id}"
    ),
    "reddit": PlatformConfig(
        "Reddit", 0xFF4500, "0", "https://www.reddit.com/user/{media_id}"
    ),
    "seiga": PlatformConfig(
        "NicoNico Seiga",
        0xEDA715,
        "0",
        "https://seiga.nicovideo.jp/user/illust/{media_id}",
    ),
    "tumblr": PlatformConfig("Tumblr", 0x35465C, "0", "https://{media_id}.tumblr.com"),
    "twitter": PlatformConfig(
        "Twitter", 0x15202B, "0", "https://twitter.com/{media_id}"
    ),
    "weibo": PlatformConfig("Weibo", 0xE6162D, "0", "https://weibo.com/{media_id}"),
    # Media tracking
    "allcin": PlatformConfig(
        "AllCinema",
        0xEC0A0A,
        "1079493870326403123",
        "https://www.allcinema.net/prog/show_c.php?num_c={media_id}",
    ),
    "anidb": PlatformConfig(
        "AniDB", 0x2A2F46, "1073439145067806801", "https://anidb.net/anime/{media_id}"
    ),
    "anilist": PlatformConfig(
        "AniList",
        0x2F80ED,
        "1073445700689465374",
        "https://anilist.co/anime/{media_id}",
    ),
    "animeplanet": PlatformConfig(
        "Anime-Planet",
        0xE75448,
        "1073446927447891998",
        "https://www.anime-planet.com/anime/{media_id}",
    ),
    "anisearch": PlatformConfig(
        "AniSearch",
        0xFDA37C,
        "1073439148100300810",
        "https://anisearch.com/anime/{media_id}",
    ),
    "animenewsnetwork": PlatformConfig(
        "Anime News Network",
        0x2D50A7,
        "1079377192951230534",
        "https://www.animenewsnetwork.com/encyclopedia/anime.php?id={media_id}",
    ),
    "annict": PlatformConfig(
        "Annict (アニクト)",
        0xF65B73,
        "1088801941469012050",
        "https://en.annict.com/works/{media_id}",
    ),
    "imdb": PlatformConfig(
        "IMDb", 0xF5C518, "1079376998880784464", "https://www.imdb.com/title/{media_id}"
    ),
    "kaize": PlatformConfig(
        "Kaize", 0x692FC2, "1073441859910774784", "https://kaize.io/anime/{media_id}"
    ),
    "kitsu": PlatformConfig(
        "Kitsu", 0xF85235, "1073439152462368950", "https://kitsu.app/anime/{media_id}"
    ),
    "lastfm": PlatformConfig(
        "Last.fm", 0xD51007, "0", "https://www.last.fm/user/{media_id}"
    ),
    "letterboxd": PlatformConfig(
        "Letterboxd", 0x202830, "0", "https://letterboxd.com/film/{media_id}"
    ),
    "livechart": PlatformConfig(
        "LiveChart",
        0x67A427,
        "1073439158883844106",
        "https://livechart.me/anime/{media_id}",
    ),
    "myanimelist": PlatformConfig(
        "MyAnimeList",
        0x2F51A3,
        "1073442204921643048",
        "https://myanimelist.net/anime/{media_id}",
    ),
    "nautiljon": PlatformConfig(
        "Nautiljon",
        0xECB253,
        "1144533712818667640",
        "https://www.nautiljon.com/animes/{media_id}.html",
    ),
    "notify": PlatformConfig(
        "Notify.moe",
        0xDEA99E,
        "1073439161194905690",
        "https://notify.moe/anime/{media_id}",
    ),
    "otakotaku": PlatformConfig(
        "Otak Otaku",
        0xBE2222,
        "1088801946313429013",
        "https://otakotaku.com/anime/view/{media_id}",
    ),
    "shikimori": PlatformConfig(
        "Shikimori (Шикимори)",
        0x2E2E2E,
        "1073441855645155468",
        "https://shikimori.one/animes/{media_id}",
    ),
    "shoboi": PlatformConfig(
        "Shoboi Calendar (しょぼいカレンダー)",
        0xE3F0FD,
        "1088801950751015005",
        "https://cal.syoboi.jp/tid/{media_id}",
    ),
    "silveryasha": PlatformConfig(
        "SilverYasha",
        0x0172BB,
        "1079380182059733052",
        "https://db.silveryasha.web.id/anime/{media_id}",
    ),
    "simkl": PlatformConfig(
        "SIMKL",
        0x0B0F10,
        "1073630754275348631",
        "https://simkl.com/{simkl_type}/{media_id}",
    ),
    "tmdb": PlatformConfig(
        "The Movie Database",
        0x09B4E2,
        "1079379319920529418",
        "https://www.themoviedb.org/{media_id}",
    ),
    "trakt": PlatformConfig(
        "Trakt", 0xED1C24, "1081612822175305788", "https://trakt.tv/{media_id}"
    ),
    "tvdb": PlatformConfig("The TVDB", 0x6CD491, "1079378495064510504", "{media_id}"),
    "tvtime": PlatformConfig(
        "TV Time", 0xFFD80A, "1091550459023605790", "https://tvtime.com/en/{media_id}"
    ),
}


def get_platform_color(pf: str | Platform) -> int:
    """
    Get a color code for a specific platform

    Args:
        pf (str | Platform): The platform to get the color code for.

    Returns:
        int: The color code for the platform, or 0x000000 if the platform is not supported.
    """
    if isinstance(pf, str):
        pf = Platform(pf)
    config = PLATFORM_CONFIGS.get(pf.value)
    return config.color if config else 0x000000


def get_platform_name(pf: str | Platform) -> str:
    """
    Get a platform name from its abbreviation

    Args:
        pf (str | Platform): The platform to get the name for.

    Returns:
        str: The name of the platform, or "Unknown" if the platform is not supported.
    """
    if isinstance(pf, str):
        pf = Platform(pf)
    config = PLATFORM_CONFIGS.get(pf.value)
    return config.name if config else "Unknown"


def media_id_to_platform(
    media_id: str, platform: str | Platform, simkl_type: Union[str, None] = None
) -> PlatformLink:
    """
    Convert a media ID to a platform-specific ID

    Args:
        media_id (str): The media ID to convert
        platform (str | Platform): The platform to convert the ID to
        simkl_type (Union[str, None], optional): The type of media to convert the ID to. Defaults to None.

    Raises:
        ValueError: If the platform is not supported

    Returns:
        PlatformLink: An object containing the converted ID and the emoji ID for the platform
    """
    if isinstance(platform, str):
        platform = Platform(platform)

    config = PLATFORM_CONFIGS.get(platform.value)
    if not config:
        raise ValueError(f"Invalid platform: {platform}")

    url = config.url_template.format(media_id=media_id, simkl_type=simkl_type)

    return PlatformLink(pf=config.name, uid=url, emoid=config.emoji_id)


def platforms_to_fields(currPlatform: str, **k: str | None) -> list[EmbedField]:
    """Convert a platform to a dictionary of fields"""
    relsEm: list[dict[str, Any]] = []

    platform_mappings = {
        "allcin": "allcin",
        "anidb": "anidb",
        "anilist": "anilist",
        "ann": "animenewsnetwork",
        "animenewsnetwork": "animenewsnetwork",
        "animeplanet": "animeplanet",
        "anisearch": "anisearch",
        "annict": "annict",
        "imdb": "imdb",
        "kaize": "kaize",
        "kitsu": "kitsu",
        "letterboxd": "letterboxd",
        "livechart": "livechart",
        "myanimelist": "myanimelist",
        "nautiljon": "nautiljon",
        "notify": "notify",
        "otakotaku": "otakotaku",
        "shikimori": "shikimori",
        "shoboi": "shoboi",
        "silveryasha": "silveryasha",
        "simkl": "simkl",
        "trakt": "trakt",
        "tmdb": "tmdb",
        "tvdb": "tvdb",
    }

    for platform, value in k.items():
        try:
            if value is not None and currPlatform != platform:
                pin = media_id_to_platform(
                    value, platform_mappings[platform], simkl_type=k["simkl_type"]
                )
                if platform == "tvdb":
                    value = str(value).removeprefix("https://www.thetvdb.com/")
                relsEm.append(
                    {
                        "name": f"<:{platform_mappings[platform]}:{pin.emoid}> {pin.pf}",
                        "value": f"[{value}](<{pin.uid}>)",
                        "inline": True,
                    }
                )
        except KeyError:
            continue

    if k["tvtime"] is not None:
        media_id = k["tvtime"]
        pin = media_id_to_platform(media_id=media_id, platform="tvtime")
        relsEm.append(
            {
                "name": f"<:tvTime:{pin.emoid}> {pin.pf}",
                "value": f"[{media_id}](<{pin.uid}>)",
                "inline": True,
            }
        )

    # sort the list by platform name
    relsEm = sorted(relsEm, key=lambda k: k["name"])

    # convert the list of dicts to a list of EmbedFields
    result = [EmbedField(**x) for x in relsEm]

    return result
