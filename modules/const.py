import subprocess
from os import getenv as ge
from typing import Final

from dotenv import load_dotenv as ld

from modules.commons import *

ld()

database = r"database/database.csv"

AUTHOR_USERID: Final[int] = ge('AUTHOR_USERID')
AUTHOR_USERNAME: Final[str] = ge('AUTHOR_USERNAME')
BOT_CLIENT_ID: Final[int] = ge('BOT_CLIENT_ID')
BOT_SUPPORT_SERVER: Final[str] = ge('BOT_SUPPORT_SERVER')
BOT_TOKEN: Final[str] = ge('BOT_TOKEN')
CLUB_ID: Final[int] = ge('CLUB_ID')
LASTFM_API_KEY: Final[str] = ge('LASTFM_API_KEY')
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


def get_git_revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()


def get_git_revision_short_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


gittyHash = get_git_revision_hash()
gtHsh = get_git_revision_short_hash()

# =============================================================================
# About Bot

ownerUserUrl = f'https://discord.com/users/{AUTHOR_USERID}'

ABOUT_BOT: Final[str] = f'''<@!{BOT_CLIENT_ID}> is a bot personally created and used by [nattadasu](<https://nattadasu.my.id>) with the initial purpose as for member verification and MAL profile integration bot, which is distributed under [AGPL 3.0](<https://www.gnu.org/licenses/agpl-3.0.en.html>) license. ([Source Code](<https://github.com/nattadasu/ryuuRyuusei>), source code in repository may be older than main production maintained by nattadasu for)

However, due to how advanced the bot in querying information regarding user, anime on MAL, and manga on AniList, invite link is available for anyone who's interested to invite the bot (see `/invite`).

This bot may requires your consent to collect and store your data when you invoke `/register` command. You can see the privacy policy by using `/privacy` command.

However, you still able to use the bot without collecting your data, albeit limited usage.

If you want to contact the author, send a DM to [{AUTHOR_USERNAME}](<{ownerUserUrl}>) or via [support server](<{BOT_SUPPORT_SERVER}>).

Bot version, in Git hash: [`{gtHsh}`](<https://github.com/nattadasu/ryuuRyuusei/commit/{gittyHash}>)
'''

# =============================================================================
# Privacy Policy

PRIVACY_POLICY: Final[str] = '''Hello and thank you for your interest to read this tl;dr version of Privacy Policy.

In this message we shortly briefing which content we collect, store, and use, including what third party services we used for bot to function as expected. You can read the full version of [Privacy Policy here at anytime you wish](<https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md>).

__We collect, store, and use following data__:
- Discord: username, discriminator, user snowflake ID, joined date, guild/server ID of registration, server name, date of registration, user referral (if any)
- MyAnimeList: username, user ID, joined date

__We shared limited personal information about you to 3rd Party__:
This is required for the bot to function as expected, with the following services:
Discord, Last.FM, MAL Heatmap, MyAnimeList

__We cached data for limited features of the bot__:
Used to reduce the amount of API calls to 3rd party services, and to reduce the amount of time to process the data and no information tied to you.

__We do not collect, however, following data__:
Any logs of messages sent by system about you under any circumstances. Logging of messages only occurs when you invoked general commands (such as `/help`, `/anime`, `/manga`, etc.) and during the bot's development process. Maintenance will announced in the Bot status channel in Support Server and Bot Activity.

Data stored locally to Data Maintainer's (read: owner) server/machine of this bot as CSV. To read your profile that we've collected, type `/export_data` following your username.

As user, you have right to access, know, data portability, modify/rectify, delete, restrict, limit, opt-out, and/or withdraw your consent to use your data.

For any contact information, type `/about`.'''

# =============================================================================
# Support Development

SUPPORT_DEVELOPMENT: Final[str] = f'''{EMOJI_ATTENTIVE} Thanks for your interest in supporting me!

You can support me on [Ko-Fi](<https://ko-fi.com/nattadasu>), [PayPal](<https://paypal.me/nattadasu>), or [GitHub Sponsors](<https://github.com/sponsors/nattadasu>).

For Indonesian users, you can use [Trakteer](<https://trakteer.id/nattadasu>) or [Saweria](<https://saweria.co/nattadasu>).

Or, are you a developer? You can contribute to the bot's code on [GitHub](<https://github.com/nattadasu/ryuuRyuusei>)

If you have any questions (or more payment channels), please join my [support server]({BOT_SUPPORT_SERVER})!'''

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

ERR_KAIZE_SLUG_MODDED: Final[str] = '''We've tried to search for the anime using the slug (and even fix the slug itself), but it seems that the anime is not found on Kaize via AnimeApi.
Please send a message to AnimeApi maintainer, nattadasu (he is also a developer of this bot)'''

# =============================================================================
# Aliases

warnThreadCW = MESSAGE_WARN_CONTENTS
