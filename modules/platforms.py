from collections import defaultdict
from enum import Enum
from typing import Union

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
    ANIMENEWSNETWORK = ANN = "ann"
    ANIMEPLANET = AP = "animeplanet"
    ANISEARCH = AS = "anisearch"
    ANNICT = "annict"
    IMDB = "imdb"
    KAIZE = "kaize"
    KITSU = "kitsu"
    LASTFM = LAST = LFM = "lastfm"
    LIVECHART = LC = "livechart"
    MYANIMELIST = MAL = "myanimelist"
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


def get_platform_color(pf: str | Platform) -> hex:
    """
    Get a color code for a specific platform

    Args:
        pf (str | Platform): The platform to get the color code for.

    Returns:
        hex: The color code for the platform, or 0x000000 if the platform is not supported.
    """
    if isinstance(pf, str):
        pf = Platform(pf)
    pfDict = defaultdict(
        lambda: 0x000000,
        {
            # SNS
            "artstation": 0x0F0F0F,
            "deviantart": 0x05CC47,
            "discord": 0x7289DA,
            "facebook": 0x3B5998,
            "flickr": 0xFF0084,
            "hoyolab": 0x1B75BB,
            "instagram": 0x833AB4,
            "lofter": 0x335F60,
            "patreon": 0xF96854,
            "pixiv": 0x0096FA,
            "reddit": 0xFF4500,
            "seiga": 0xEDA715,
            "tumblr": 0x35465C,
            "twitter": 0x15202B,
            "weibo": 0xE6162D,
            # Media tracking
            "allcin": 0xEC0A0A,
            "anidb": 0x2A2F46,
            "anilist": 0x2F80ED,
            "animeplanet": 0xE75448,
            "anisearch": 0xFDA37C,
            "ann": 0x2D50A7,
            "annict": 0xF65B73,
            "imdb": 0xF5C518,
            "kaize": 0x692FC2,
            "kitsu": 0xF85235,
            "lastfm": 0xD51007,
            "livechart": 0x67A427,
            "myanimelist": 0x2F51A3,
            "notify": 0xDEA99E,
            "otakotaku": 0xBE2222,
            "shikimori": 0x2E2E2E,
            "shoboi": 0xE3F0FD,
            "silveryasha": 0x0172BB,
            "simkl": 0x0B0F10,
            "syoboi": 0xE3F0FD,
            "tmdb": 0x09B4E2,
            "trakt": 0xED1C24,
            "tvdb": 0x6CD491,
            "tvtime": 0xFBD737,
        },
    )

    return pfDict[pf.value]


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
    pfDict = {
        # SNS
        "artstation": "ArtStation",
        "deviantart": "DeviantArt",
        "discord": "Discord",
        "facebook": "Facebook",
        "flickr": "Flickr",
        "hoyolab": "Hoyolab",
        "instagram": "Instagram",
        "lofter": "Lofter",
        "patreon": "Patreon",
        "pixiv": "Pixiv",
        "reddit": "Reddit",
        "seiga": "NicoNico Seiga",
        "tumblr": "Tumblr",
        "twitter": "Twitter",
        "weibo": "Weibo",
        # Media tracking
        "allcin": "AllCinema",
        "anidb": "AniDB",
        "anilist": "AniList",
        "animeplanet": "Anime-Planet",
        "anisearch": "AniSearch",
        "ann": "Anime News Network",
        "annict": "Annict (アニクト)",
        "imdb": "IMDb",
        "kaize": "Kaize",
        "kitsu": "Kitsu",
        "lastfm": "Last.fm",
        "livechart": "LiveChart",
        "myanimelist": "MyAnimeList",
        "notify": "Notify.moe",
        "otakotaku": "Otak Otaku",
        "shikimori": "Shikimori (Шикимори)",
        "shoboi": "Shoboi Calendar (しょぼいカレンダー)",
        "silveryasha": "SilverYasha",
        "simkl": "SIMKL",
        "tmdb": "The Movie Database",
        "trakt": "Trakt",
        "tvdb": "The TVDB",
        "tvtime": "TV Time",
    }

    return pfDict.get(pf.value, "Unknown")


def media_id_to_platform(
    media_id: str,
    platform: str | Platform,
    simkl_type: Union[str, None] = None
) -> dict:
    """
    Convert a media ID to a platform-specific ID

    Args:
        media_id (str): The media ID to convert
        platform (str | Platform): The platform to convert the ID to
        simkl_type (Union[str, None], optional): The type of media to convert the ID to. Defaults to None.

    Raises:
        ValueError: If the platform is not supported

    Returns:
        dict: A dictionary containing the converted ID and the emoji ID for the platform
    """
    if isinstance(platform, str):
        platform = Platform(platform)
    platform_dict = {
        "anidb": {
            "uid": f"https://anidb.net/anime/{media_id}",
            "emoid": "1073439145067806801",
        },
        "anilist": {
            "uid": f"https://anilist.co/anime/{media_id}",
            "emoid": "1073445700689465374",
        },
        "animeplanet": {
            "uid": f"https://www.anime-planet.com/anime/{media_id}",
            "emoid": "1073446927447891998",
        },
        "anisearch": {
            "uid": f"https://anisearch.com/anime/{media_id}",
            "emoid": "1073439148100300810",
        },
        "annict": {
            "uid": f"https://en.annict.com/works/{media_id}",
            "emoid": "1088801941469012050",
        },
        "imdb": {
            "uid": f"https://www.imdb.com/title/{media_id}",
            "emoid": "1079376998880784464",
        },
        "kaize": {
            "uid": f"https://kaize.io/anime/{media_id}",
            "emoid": "1073441859910774784",
        },
        "kitsu": {
            "uid": f"https://kitsu.io/anime/{media_id}",
            "emoid": "1073439152462368950",
        },
        "myanimelist": {
            "uid": f"https://myanimelist.net/anime/{media_id}",
            "emoid": "1073442204921643048",
        },
        "shikimori": {
            "uid": f"https://shikimori.one/animes/{media_id}",
            "emoid": "1073441855645155468",
        },
        "livechart": {
            "uid": f"https://livechart.me/anime/{media_id}",
            "emoid": "1073439158883844106",
        },
        "notify": {
            "uid": f"https://notify.moe/anime/{media_id}",
            "emoid": "1073439161194905690",
        },
        "otakotaku": {
            "uid": f"https://otakotaku.com/anime/view/{media_id}",
            "emoid": "1088801946313429013",
        },
        "simkl": {
            "uid": f"https://simkl.com/{simkl_type}/{media_id}",
            "emoid": "1073630754275348631",
        },
        "shoboi": {
            "uid": f"https://cal.syoboi.jp/tid/{media_id}",
            "emoid": "1088801950751015005",
        },
        "tmdb": {
            "uid": f"https://www.themoviedb.org/{media_id}",
            "emoid": "1079379319920529418",
        },
        "silveryasha": {
            "uid": f"https://db.silveryasha.web.id/anime/{media_id}",
            "emoid": "1079380182059733052",
        },
        "trakt": {
            "uid": f"https://trakt.tv/{media_id}",
            "emoid": "1081612822175305788",
        },
        "tvdb": {"uid": media_id, "emoid": "1079378495064510504"},
        "allcin": {
            "uid": f"https://www.allcinema.net/prog/show_c.php?num_c={media_id}",
            "emoid": "1079493870326403123",
        },
        "ann": {
            "uid": f"https://www.animenewsnetwork.com/encyclopedia/anime.php?id={media_id}",
            "emoid": "1079377192951230534",
        },
        "tvtime": {
            "uid": f"https://tvtime.com/en/{media_id}",
            "emoid": "1091550459023605790",
        },
    }

    try:
        data = platform_dict[platform.value]
        data["pf"] = get_platform_name(platform.value)

        return data
    except KeyError:
        raise ValueError(f"Invalid platform: {platform}")


def platforms_to_fields(
        currPlatform: str,
        **k: str | None) -> list[EmbedField]:
    """Convert a platform to a dictionary of fields"""
    relsEm: list[dict[str, dict[str, str | bool]]] = []

    platform_mappings = {
        "allcin": "allcin",
        "anidb": "anidb",
        "anilist": "anilist",
        "ann": "ann",
        "animeplanet": "animeplanet",
        "anisearch": "anisearch",
        "annict": "annict",
        "imdb": "imdb",
        "kaize": "kaize",
        "kitsu": "kitsu",
        "livechart": "livechart",
        "myanimelist": "myanimelist",
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
                    value, platform_mappings[platform], simkl_type=k["simkl_type"])
                if platform == "tvdb":
                    value = str(value).removeprefix("https://www.thetvdb.com/")
                relsEm.append(
                    {
                        "name": f"<:{platform_mappings[platform]}:{pin['emoid']}> {pin['pf']}",
                        "value": f"[{value}](<{pin['uid']}>)",
                        "inline": True,
                    })
        except KeyError:
            continue

    if k["tvtime"] is not None:
        media_id = k["tvtime"]
        pin = media_id_to_platform(media_id=media_id, platform="tvtime")
        relsEm.append(
            {
                "name": f"<:tvTime:{pin['emoid']}> {pin['pf']}",
                "value": f"[{media_id}](<{pin['uid']}>)",
                "inline": True,
            }
        )

    # sort the list by platform name
    relsEm = sorted(relsEm, key=lambda k: k["name"])

    # convert the list of dicts to a list of EmbedFields
    result = [EmbedField(**x) for x in relsEm]

    return result
