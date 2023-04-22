"""# Constants and Variables Module

This module contains all constants used in the bot.

All constants are stored in a .env file. The .env file is not included in the repository for security reasons.
However, you can use the .env.example file as a template to create your own .env file.

This module also contains some mutable variables/constant that are used oftenly in the bot."""

from os import getenv as ge
from subprocess import check_output as chout
from typing import Final

from dotenv import load_dotenv as ld

__version__: Final[str] = "1.0.0"

ld()

database = r"database/database.csv"

AUTHOR_USERID: Final[int] = ge('AUTHOR_USERID')
AUTHOR_USERNAME: Final[str] = ge('AUTHOR_USERNAME')
BOT_CLIENT_ID: Final[int] = ge('BOT_CLIENT_ID')
BOT_SUPPORT_SERVER: Final[str] = ge('BOT_SUPPORT_SERVER')
BOT_TOKEN: Final[str] = ge('BOT_TOKEN')
CLUB_ID: Final[int] = ge('CLUB_ID')
LASTFM_API_KEY: Final[str] = ge('LASTFM_API_KEY')
MYANIMELIST_CLIENT_ID: Final[str] = ge('MYANIMELIST_CLIENT_ID')
RAWG_API_KEY: Final[str] = ge('RAWG_API_KEY')
SENTRY_DSN: Final[str] = ge('SENTRY_DSN')
SIMKL_CLIENT_ID: Final[str] = ge('SIMKL_CLIENT_ID')
TMDB_API_KEY: Final[str] = ge('TMDB_API_KEY')
TMDB_API_VERSION: Final[int] = ge('TMDB_API_VERSION')
TRAKT_API_VERSION: Final[int] = ge('TRAKT_API_VERSION')
TRAKT_CLIENT_ID: Final[str] = ge('TRAKT_CLIENT_ID')
VERIFICATION_SERVER: Final[int] = ge('VERIFICATION_SERVER')
VERIFIED_ROLE: Final[int] = ge('VERIFIED_ROLE')

EMOJI_ATTENTIVE: Final[str] = ge('EMOJI_ATTENTIVE')
EMOJI_DOUBTING: Final[str] = ge('EMOJI_DOUBTING')
EMOJI_FORBIDDEN: Final[str] = ge('EMOJI_FORBIDDEN')
EMOJI_SUCCESS: Final[str] = ge('EMOJI_SUCCESS')
EMOJI_UNEXPECTED_ERROR: Final[str] = ge('EMOJI_UNEXPECTED_ERROR')
EMOJI_USER_ERROR: Final[str] = ge('EMOJI_USER_ERROR')

LANGUAGE_CODE: Final[str] = ge('LANGUAGE_CODE')


def get_git_revision_hash() -> str:
    return chout(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()


def get_git_revision_short_hash() -> str:
    return chout(['git', 'rev-parse', '--short', 'HEAD']
                 ).decode('ascii').strip()


gittyHash = get_git_revision_hash()
gtHsh = get_git_revision_short_hash()

# =============================================================================
# About Bot

ownerUserUrl = f'https://discord.com/users/{AUTHOR_USERID}'

# =============================================================================
# Declined GDPR notice

DECLINED_GDPR: Final[str] = '''**You have not accepted the GDPR/CCPA/CPRA Privacy Consent!**
Unfortunately, we cannot register you without your consent. However, you can still use the bot albeit limited.

Allowed commands:
- `/profile mal_username:<str>`
- `/ping`

If you want to register, please use the command `/register` again and accept the consent by set the `accept_gdpr` option to `true`!

We only store your MAL username, MAL UID, Discord username, Discord UID, and joined date for both platforms, also server ID during registration.
We do not store any other data such as your email, password, or any other personal information.
We also do not share your data with any third party than necessary, and it only limited to the required platforms such Username.

***We respect your privacy.***

For more info what do we collect and use, use `/privacy`.
'''

# =============================================================================

# Common errors and messages

MESSAGE_MEMBER_REG_PROFILE: Final[str] = f"{EMOJI_DOUBTING} **You are looking at your own profile!**\nYou can also use </profile:1072608801334755529> without any arguments to get your own profile!"

MESSAGE_INVITE: Final[str] = "To invite me, simply press \"**Invite me!**\" button below!\nFor any questions, please join my support server!"

MESSAGE_SELECT_TIMEOUT: Final[str] = "*Selection menu has reached timeout, please try again if you didn't pick the option!*"

MESSAGE_WARN_CONTENTS: Final[str] = f"""

If you invoked this command outside (public or private) forum thread channel or regular text channel and **Age Restriction** is enabled, please contact developer of this bot as the feature only tested in forum thread and text channel.

You can simply access it on `/support`"""

ERR_KAIZE_SLUG_MODDED: Final[
    str] = '''We've tried to search for the anime using the slug (and even fix the slug itself), but it seems that the anime is not found on Kaize via AnimeApi.
Please send a message to AnimeApi maintainer, nattadasu (he is also a developer of this bot)'''

# =============================================================================
# Aliases

warnThreadCW = MESSAGE_WARN_CONTENTS

bannedTags = [
    'Amputation', 'Anal Sex', 'Ashikoki', 'Asphyxiation',
    'Blackmail', 'Bondage', 'Boobjob', 'Cumflation',
    'Cunnilingus', 'Deepthroat', 'DILF', 'Fellatio',
    'Femdom', 'Futanari', 'Group Sex', 'Handjob',
    'Human Pet', 'Incest', 'Inseki', 'Irrumatio',
    'Lactation', 'Masochism', 'Masturbation', 'MILF',
    'Nakadashi', 'Pregnant', 'Prostitution', 'Public Sex',
    'Rape', 'Rimjob', 'Sadism', 'Scat',
    'Scissoring', 'Sex Toys', 'Squirting', 'Sumata',
    'Sweat', 'Tentacles', 'Threesome', 'Vore',
    'Voyeur', 'Watersports', 'Omegaverse'
]

invAa = {
    'title': None,
    'anidb': None,
    'anilist': None,
    'animeplanet': None,
    'anisearch': None,
    'annict': None,
    'kaize': None,
    'kitsu': None,
    'livechart': None,
    'myanimelist': None,
    'notify': None,
    'otakotaku': None,
    'shikimori': None,
    'shoboi': None,
    'silveryasha': None,
    'trakt': None,
    'trakt_type': None,
    'trakt_season': None
}

simkl0rels = {
    'title': None,
    "simkl": None,
    "slug": None,
    "poster": None,
    "fanart": None,
    "anitype": "tv",
    "type": "anime",
    "allcin": None,
    "anfo": None,
    "anidb": None,
    "anilist": None,
    "animeplanet": None,
    "anisearch": None,
    "ann": None,
    "hulu": None,
    "imdb": None,
    "kitsu": None,
    "livechart": None,
    "mal": None,
    "netflix": None,
    "offjp": None,
    "tmdb": None,
    "tvdb": None,
    "tvdbslug": None,
    "wikien": None,
    "wikijp": None,
}

traktHeader = {
    'Content-Type': 'applications/json',
    'trakt-api-key': TRAKT_CLIENT_ID,
    'trakt-api-version': TRAKT_API_VERSION
}
