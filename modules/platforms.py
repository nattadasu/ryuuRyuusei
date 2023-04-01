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
