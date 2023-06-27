"""
# Constants and Variables Module

This module contains all constants used in the bot.

All constants are stored in a .env file. The .env file is not included in the repository for security reasons.
However, you can use the .env.example file as a template to create your own .env file.

This module also contains some mutable variables/constant that are used oftenly in the bot.
"""

from os import getenv as ge
from subprocess import check_output as chout
from typing import Final, cast

from dotenv import load_dotenv as ld

__version__: Final[str] = "1.0.0"

ld()

database = r"database/database.csv"


ANILIST_CLIENT_ID: Final[str] = cast(str, ge("ANILIST_CLIENT_ID"))
"""AniList client ID"""
ANILIST_CLIENT_SECRET: Final[str] = cast(str, ge("ANILIST_CLIENT_SECRET"))
"""AniList client secret"""
ANILIST_REDIRECT_URI: Final[str] = cast(str, ge("ANILIST_REDIRECT_URI"))
"""AniList redirect URI"""
ANILIST_ACCESS_TOKEN: Final[str] = cast(str, ge("ANILIST_ACCESS_TOKEN"))
"""AniList access token"""
ANILIST_OAUTH_REFRESH: Final[str] = cast(str, ge("ANILIST_OAUTH_REFRESH"))
"""AniList OAuth refresh token"""
ANILIST_OAUTH_EXPIRY: Final[int] = cast(int, ge("ANILIST_OAUTH_EXPIRY"))
"""AniList OAuth expiry time, in seconds"""
AUTHOR_USERID: Final[int] = cast(int, ge("AUTHOR_USERID"))
"""The bot author's user ID"""
AUTHOR_USERNAME: Final[str] = cast(str, ge("AUTHOR_USERNAME"))
"""The bot author's username"""
BOT_CLIENT_ID: Final[int] = cast(int, ge("BOT_CLIENT_ID"))
"""The bot's client ID"""
BOT_SUPPORT_SERVER: Final[str] = cast(str, ge("BOT_SUPPORT_SERVER"))
"""The bot's support server invite link"""
BOT_TOKEN: Final[str] = cast(str, ge("BOT_TOKEN"))
"""The bot's token"""
CLUB_ID: Final[int] = cast(int, ge("CLUB_ID"))
"""MyAnimeList club ID"""
EXCHANGERATE_API_KEY: Final[str] = cast(str, ge("EXCHANGERATE_API_KEY"))
"""ExchangeRateAPI key"""
LASTFM_API_KEY: Final[str] = cast(str, ge("LASTFM_API_KEY"))
"""Last.fm API key"""
MYANIMELIST_CLIENT_ID: Final[str] = cast(str, ge("MYANIMELIST_CLIENT_ID"))
"""MyAnimeList client ID"""
RAWG_API_KEY: Final[str] = cast(str, ge("RAWG_API_KEY"))
"""RAWG API key"""
SENTRY_DSN: Final[str] = cast(str, ge("SENTRY_DSN"))
"""Sentry DSN"""
SHIKIMORI_CLIENT_ID: Final[str] = cast(str, ge("SHIKIMORI_CLIENT_ID"))
"""Shikimori client ID"""
SHIKIMORI_CLIENT_SECRET: Final[str] = cast(str, ge("SHIKIMORI_CLIENT_SECRET"))
"""Shikimori client secret"""
SHIKIMORI_APPLICATION_NAME: Final[str] = cast(
    str, ge("SHIKIMORI_APPLICATION_NAME"))
"""Shikimori application name"""
SIMKL_CLIENT_ID: Final[str] = cast(str, ge("SIMKL_CLIENT_ID"))
"""SIMKL client ID"""
SPOTIFY_CLIENT_ID: Final[str] = cast(str, ge("SPOTIFY_CLIENT_ID"))
"""Spotify client ID"""
SPOTIFY_CLIENT_SECRET: Final[str] = cast(str, ge("SPOTIFY_CLIENT_SECRET"))
"""Spotify client secret"""
TMDB_API_KEY: Final[str] = cast(str, ge("TMDB_API_KEY"))
"""TMDB API key"""
TMDB_API_VERSION: Final[int] = cast(int, ge("TMDB_API_VERSION"))
"""TMDB API version"""
TOPGG_API_TOKEN: Final[str] = cast(str, ge("TOPGG_API_TOKEN"))
"""Top.gg API token"""
TRAKT_API_VERSION: Final[int] = cast(int, ge("TRAKT_API_VERSION"))
"""Trakt API version"""
TRAKT_CLIENT_ID: Final[str] = cast(str, ge("TRAKT_CLIENT_ID"))
"""Trakt client ID"""
VERIFICATION_SERVER: Final[int] = cast(int, ge("VERIFICATION_SERVER"))
"""Verification server ID"""
VERIFIED_ROLE: Final[int] = cast(int, ge("VERIFIED_ROLE"))
"""Verified role ID"""

EMOJI_ATTENTIVE: Final[str] = cast(str, ge("EMOJI_ATTENTIVE"))
"""The attentive emoji"""
EMOJI_DOUBTING: Final[str] = cast(str, ge("EMOJI_DOUBTING"))
"""The doubting emoji"""
EMOJI_FORBIDDEN: Final[str] = cast(str, ge("EMOJI_FORBIDDEN"))
"""The forbidden emoji"""
EMOJI_SUCCESS: Final[str] = cast(str, ge("EMOJI_SUCCESS"))
"""The success emoji"""
EMOJI_UNEXPECTED_ERROR: Final[str] = cast(str, ge("EMOJI_UNEXPECTED_ERROR"))
"""The unexpected error emoji"""
EMOJI_USER_ERROR: Final[str] = cast(str, ge("EMOJI_USER_ERROR"))
"""The user error emoji"""

LANGUAGE_CODE: Final[str] = cast(str, ge("LANGUAGE_CODE"))
"""Default language code"""


def get_git_revision_hash() -> str:
    """
    Get the current git revision hash

    Returns:
        str: The current git revision hash
    """
    return chout(["git", "rev-parse", "HEAD"]).decode("ascii").strip()


def get_git_revision_short_hash() -> str:
    """
    Get the current git revision short hash

    Returns:
        str: The current git revision short hash
    """
    return chout(["git", "rev-parse", "--short", "HEAD"]
                 ).decode("ascii").strip()


def get_git_remote_url() -> str:
    """
    Get the URL of the origin remote

    Returns:
        str: The URL of the origin remote
    """
    output = chout(["git", "remote", "get-url", "origin"]).decode("utf-8")
    output = output.strip()
    return output


def get_current_git_branch() -> str:
    """
    Get the current git branch

    Returns:
        str: The current git branch
    """
    output = chout(["git", "branch", "--show-current"]).decode("utf-8")
    output = output.strip()
    return output


# Call the get_current_git_branch() funct


git_remote = get_git_remote_url()
"""The git remote URL"""
git_branch = get_current_git_branch()
"""The git branch"""
gittyHash = get_git_revision_hash()
"""The git revision hash"""
gtHsh = get_git_revision_short_hash()
"""The git revision short hash"""

USER_AGENT: Final[
    str
] = f"RyuuzakiRyuusei/1.0 ({git_remote}/{gtHsh}; branch:{git_branch}; author:{AUTHOR_USERNAME}:{AUTHOR_USERID}; https://discord.com/users/{BOT_CLIENT_ID})"
"""The user agent"""

# =============================================================================
# About Bot

ownerUserUrl = f"https://discord.com/users/{AUTHOR_USERID}"
"""The bot author's user URL"""

# =============================================================================
# Declined GDPR notice

DECLINED_GDPR: Final[
    str
] = """## You have not accepted the Privacy Policy!
Unfortunately, we cannot register you without your consent. However, you can still use the bot albeit limited.

Allowed commands:
- `/profile myanimelist mal_username:<str>`
- `/profile anilist anilist_username:<str>`
- `/profile shikimori shikimori_username:<str>`
- `/profile lastfm lastfm_username:<str>`

If you want to register, please use the command `/register` again and accept the consent by set the `accept_privacy_policy` option to `true`!

We only store your MAL username, MAL UID, Discord username, Discord UID, and joined date for both platforms, also server ID during registration.
We do not store any other data such as your email, password, or any other personal information.
We also do not share your data with any third party than necessary, and it only limited to the required platforms such Username.

***We respect your privacy.***

For more info what do we collect and use, use `/privacy`.
"""
"""The declined GDPR notice, deprecated in favor of i18n"""

# =============================================================================

# Common errors and messages

MESSAGE_MEMBER_REG_PROFILE: Final[
    str
] = f"{EMOJI_DOUBTING} **You are looking at your own profile!**\nYou can also use </profile:1072608801334755529> without any arguments to get your own profile!"
"""The message when a user is looking at their own profile"""

MESSAGE_INVITE: Final[
    str
] = 'To invite me, simply press "**Invite me!**" button below!\nFor any questions, please join my support server!'
"""The invite message"""

MESSAGE_SELECT_TIMEOUT: Final[
    str
] = "*Selection menu has reached timeout, please try again if you didn't pick the option!*"
"""The message when a selection menu has reached timeout"""

MESSAGE_WARN_CONTENTS: Final[
    str
] = """

If you invoked this command outside (public or private) forum thread channel or regular text channel and **Age Restriction** is enabled, please contact developer of this bot as the feature only tested in forum thread and text channel.

You can simply access it on `/support`"""
"""The message when a user invoked a command outside forum thread channel or regular text channel"""

ERR_KAIZE_SLUG_MODDED: Final[
    str
] = """We've tried to search for the anime using the slug (and even fix the slug itself), but it seems that the anime is not found on Kaize via AnimeApi.
Please send a message to AnimeApi maintainer, nattadasu (he is also a developer of this bot)"""
"""The message when a slug is not found on Kaize"""

# =============================================================================
# Aliases

warnThreadCW = MESSAGE_WARN_CONTENTS
"""The alias of `MESSAGE_WARN_CONTENTS`"""

banned_tags = [
    "Amputation",
    "Anal Sex",
    "Ashikoki",
    "Asphyxiation",
    "Blackmail",
    "Bondage",
    "Boobjob",
    "Cumflation",
    "Cunnilingus",
    "Deepthroat",
    "DILF",
    "Fellatio",
    "Femdom",
    "Futanari",
    "Group Sex",
    "Handjob",
    "Human Pet",
    "Incest",
    "Inseki",
    "Irrumatio",
    "Lactation",
    "Masochism",
    "Masturbation",
    "MILF",
    "Nakadashi",
    "Pregnant",
    "Prostitution",
    "Public Sex",
    "Rape",
    "Rimjob",
    "Sadism",
    "Scat",
    "Scissoring",
    "Sex Toys",
    "Squirting",
    "Sumata",
    "Sweat",
    "Tentacles",
    "Threesome",
    "Vore",
    "Voyeur",
    "Watersports",
    "Omegaverse",
]
"""List of tags that should be removed if found on AniList result"""

traktHeader = {
    "Content-Type": "applications/json",
    "trakt-api-key": TRAKT_CLIENT_ID,
    "trakt-api-version": TRAKT_API_VERSION,
}
"""Default Trakt API header"""
