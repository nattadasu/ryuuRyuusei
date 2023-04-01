def getPlatformColor(pf: str) -> hex:
    """Get a color code for a specific platform"""
    pf = pf.lower()
    if pf == "syoboi":
        pf = "shoboi"
    elif pf == "last":
        pf = "lastfm"
    pfDict = {
        # SNS
        "artstation": 0x0F0F0F,
        "deviantart": 0x05CC47,
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
        "anidb": 0x2A2F46,
        "anilist": 0x2F80ED,
        "animeplanet": 0xE75448,
        "anisearch": 0xFDA37C,
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
    }

    return pfDict.get(pf, 0x000000)


def getPlatformName(pf: str) -> str:
    """Get a platform name from its abbreviation"""
    pf = pf.lower()
    if pf == "syoboi":
        pf = "shoboi"
    pfDict = {
        # SNS
        "artstation": "ArtStation",
        "deviantart": "DeviantArt",
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
        "anidb": "AniDB",
        "anilist": "AniList",
        "animeplanet": "Anime-Planet",
        "anisearch": "AniSearch",
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
        "silveryasha": "SilverYasha",
        "simkl": "SIMKL",
        "shoboi": "Shoboi Calendar (しょぼいカレンダー)",
        "tmdb": "The Movie Database",
        "trakt": "Trakt",
        "tvdb": "The TVDB",
    }

    return pfDict.get(pf, "Unknown")

def mediaIdToPlatform(media_id: str, platform: str) -> dict:
    """Convert a media ID to a platform-specific ID"""
    platform_dict = {
        'anidb': {
            'uid': f'https://anidb.net/anime/{media_id}',
            'emoid': '1073439145067806801'},
        'anilist': {
            'uid': f'https://anilist.co/anime/{media_id}',
            'emoid': '1073445700689465374'},
        'animeplanet': {
            'uid': f'https://www.anime-planet.com/anime/{media_id}',
            'emoid': '1073446927447891998'},
        'anisearch': {
            'uid': f'https://anisearch.com/anime/{media_id}',
            'emoid': '1073439148100300810'},
        'annict': {
            'uid': f'https://en.annict.com/works/{media_id}',
            'emoid': '1088801941469012050'},
        'imdb': {
            'uid': f"https://www.imdb.com/title/{media_id}",
            'emoid': '1079376998880784464'},
        'kaize': {
            'uid': f'https://kaize.io/anime/{media_id}',
            'emoid': '1073441859910774784'},
        'kitsu': {
            'uid': f'https://kitsu.io/anime/{media_id}',
            'emoid': '1073439152462368950'},
        'myanimelist': {
            'uid': f'https://myanimelist.net/anime/{media_id}',
            'emoid': '1073442204921643048'},
        'shikimori': {
            'uid': f'https://shikimori.one/animes/{media_id}',
            'emoid': '1073441855645155468'},
        'livechart': {
            'uid': f'https://livechart.me/anime/{media_id}',
            'emoid': '1073439158883844106'},
        'notify': {
            'uid': f'https://notify.moe/anime/{media_id}',
            'emoid': '1073439161194905690'},
        'otakotaku': {
            'uid': f'https://otakotaku.com/anime/view/{media_id}',
            'emoid': '1088801946313429013'},
        'simkl': {
            'uid': f'https://simkl.com/anime/{media_id}',
            'emoid': '1073630754275348631'},
        'shoboi': {
            'uid': f'https://cal.syoboi.jp/tid/{media_id}',
            'emoid': '1088801950751015005'},
        'tmdb': {
            'uid': f"https://www.themoviedb.org/{media_id}",
            'emoid': '1079379319920529418'},
        'silveryasha': {
            'uid': f"https://db.silveryasha.web.id/anime/{media_id}",
            'emoid': "1079380182059733052"},
        'trakt': {
            'uid': f"https://trakt.tv/{media_id}",
            'emoid': '1081612822175305788'},
        'tvdb': {
            'uid': media_id,
            'emoid': '1079378495064510504'},
    }

    data = platform_dict[platform]
    data['pf'] = getPlatformName(platform)

    return data
