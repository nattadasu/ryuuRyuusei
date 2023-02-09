#!/usr/bin/env python3

# cSpell:words envvars dotenv jikan discrim Natsu tada pesannya Neko Angery simkl aiohttp anilist jikanpy myanimelist CCPA CPRA whois LGDP wumpus mangalist animelist
from dotenv import load_dotenv
from jikanpy import AioJikan
from json import loads as jload
import aiohttp
import csv
import datetime
import interactions
import json
import os
import pandas as pd

load_dotenv()

AUTHOR_USERID = os.getenv('AUTHOR_USERID')
AUTHOR_USERNAME= os.getenv('AUTHOR_USERNAME')
BOT_CLIENT_ID = os.getenv('BOT_CLIENT_ID')
BOT_SUPPORT_SERVER = os.getenv('BOT_SUPPORT_SERVER')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CLUB_ID = os.getenv('CLUB_ID')
SIMKL_CLIENT_ID = os.getenv('SIMKL_CLIENT_ID')
TRAKT_CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
VERIFICATION_SERVER = os.getenv('VERIFICATION_SERVER')
VERIFIED_ROLE = os.getenv('VERIFIED_ROLE')

EMOJI_ATTENTIVE = os.getenv('EMOJI_ATTENTIVE')
EMOJI_DOUBTING = os.getenv('EMOJI_DOUBTING')
EMOJI_FORBIDDEN = os.getenv('EMOJI_FORBIDDEN')
EMOJI_SUCCESS = os.getenv('EMOJI_SUCCESS')
EMOJI_UNEXPECTED_ERROR = os.getenv('EMOJI_UNEXPECTED_ERROR')
EMOJI_USER_ERROR = os.getenv('EMOJI_USER_ERROR')

bot = interactions.Client(
    token=BOT_TOKEN,
    presence=interactions.ClientPresence(
        since=None,
        activities=[
            interactions.PresenceActivity(
                name="members",
                type=interactions.PresenceActivityType.WATCHING,
                emoji=interactions.emoji.Emoji(
                    id=1070778287644741642,
                    name="lenSeal"
                )
            )
        ],
        status=interactions.StatusType.IDLE
    )
)
database = r"database.csv"

jikan = AioJikan()


def snowflake_to_datetime(snowflake: int) -> datetime:
    timestamp_bin = bin(int(snowflake) >> 22)
    timestamp_dec = int(timestamp_bin, 0)
    timestamp_unix = (timestamp_dec + 1420070400000) / 1000

    return timestamp_unix

# CSV Layout is:
# Discord ID, Discord Username, Discord Joined, MAL Username, MAL ID, MAL Joined


def checkIfRegistered(discordId: int) -> bool:
    with open(database, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0] == discordId:
                return True
        return False


def saveToDatabase(discordId: int, discordUsername: str, discordJoined: int, malUsername: str, malId: int, malJoined: int, registeredAt: int, registeredGuild: int, registeredBy: int):
    with open(database, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([discordId, discordUsername, discordJoined, malUsername,
                        malId, malJoined, registeredAt, registeredGuild, registeredBy])


def returnException(error: str):
    return f"""{EMOJI_UNEXPECTED_ERROR} **Error found!**
Oi, <@!384089845527478272>, ini script error loh. Pesannya:```apache
{error}```"""


async def checkClubMembership(username):
    jikanUser = await jikan.users(username=f'{username}', extension='clubs')
    return jikanUser['data']


async def getJikanData(uname):
    jikanData = await jikan.users(username=f'{uname}')
    jikanData = jikanData['data']
    return jikanData


async def searchJikanAnime(title: str):
    jikanParam = {
        'limit': '10'
    }
    jikanData = await jikan.search('anime', f'{title}', parameters=jikanParam)
    jikanData = jikanData['data']
    return jikanData


async def getJikanAnime(mal_id: int):
    id = mal_id
    jikanData = await jikan.anime(id)
    jikanData = jikanData['data']
    return jikanData


async def getNatsuAniApi(id: int, platform: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://aniapi.nattadasu.my.id/{platform}/{id}') as resp:
            jsonText = await resp.text()
            jsonFinal = jload(jsonText)
        return jsonFinal


async def searchAniList(name: str):
    url = 'https://graphql.anilist.co'
    query = '''query ($search: String, $isAdult: Boolean) {
    anime: Page(perPage: 20) {
        pageInfo {
            total
        }
        results: media(type: ANIME, isAdult: $isAdult, search: $search) {
            id
            idMal
            title {
                romaji
                english
                native
            }
            isAdult
            synonyms
        }
    }
}'''
    variables = {
        'search': name
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={'query': query, 'variables': variables}) as resp:
            jsonResult = await resp.json()
            return jsonResult['data']['anime']['results']


async def getSimklFromMal(mal_id):
    # first, lookup MAL ID and SIMKL id relation
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.simkl.com/search/id?mal={mal_id}?client_id={SIMKL_CLIENT_ID}') as resp:
            final = await resp.json()
            return final[0]['ids']['simkl']


async def getSimklAnime(simkl_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.simkl.com/anime/{simkl_id}?extended=full&client_id={SIMKL_CLIENT_ID}') as resp:
            final = await resp.json()
            return final


async def getTraktFromTMDB(tmdb_id):
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': TRAKT_CLIENT_ID
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'https://api.trakt.tv/search/tmdb/{tmdb_id}') as resp:
            jn = await resp.json()
            if jn[0]['type'] == 'movie':
                mediaType = 'movies'
                mediaId = jn[0]['movie']['ids']['trakt']
            elif jn[0]['type'] == 'show':
                mediaType = 'shows'
                mediaId = jn[0]['show']['ids']['trakt']
            final = {
                'mediaType': mediaType,
                'mediaId': mediaId
            }
            return final


def grabClubId(snowflake: int):
    snow = str(snowflake)
    # Natsu's Hell
    if (snow == "589128995501637655") or (snow == "923830321433149450"):
        return 88667
    # The Newbie Club
    elif snow == "449172244724449290":
        return 70668
    # Custom Club
    elif snow == f"{VERIFICATION_SERVER}":
        return CLUB_ID
    else:
        return 0


@bot.command(
    name="ping",
    description="Ping the bot!"
)
async def ping(ctx: interactions.CommandContext):
    await ctx.send("Pong!")


@bot.command(
    name="register",
    description="Register your MAL profile to the bot!",
    # type=interactions.InteractionType.PING,
    options=[
        interactions.Option(
            name="mal_username",
            description="Your MAL username",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="accept_gdpr",
            description="Allow the bot to store your data: MAL Uname, UID, Discord Uname, UID, Joined Date",
            type=interactions.OptionType.BOOLEAN,
            required=True
        )
    ]
)
async def register(ctx: interactions.CommandContext, mal_username: str, accept_gdpr: bool):
    # check if user accepted GDPR
    if accept_gdpr is False:
        messages = f"""**You have not accepted the GDPR/CCPA/CPRA Privacy Consent!**
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
"""
        await ctx.send(messages)
        return
    else:
        # get the message author username
        messageAuthor = ctx.user
        # get the message author id
        discordId = str(messageAuthor.id)
        # get user discriminator
        discordDiscrim = str(messageAuthor.discriminator)
        # get user joined date
        discordJoined = snowflake_to_datetime(discordId)
        discordJoined = int(discordJoined)

        clubId = grabClubId(ctx.guild_id)

        # check if user is already registered
        if checkIfRegistered(discordId):
            messages = f"""{EMOJI_DOUBTING} **You are already registered!**"""
            if str(ctx.guild_id) == f'{VERIFICATION_SERVER}':
                messages += f'''\nTo get your role back, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={clubId}>)!'''
        else:
            # get user id from jikan
            try:
                jikanUser = await getJikanData(mal_username)
                # convert joined date to epoch
                joined = datetime.datetime.strptime(
                    jikanUser['joined'], "%Y-%m-%dT%H:%M:%S+00:00")
                joined = joined.timestamp()
                # try remove decimal places from joined
                joined = int(joined)
                registered = datetime.datetime.now().timestamp()
                registered = int(registered)
                messages = f"""{EMOJI_SUCCESS} **Your account has been registered!** :tada:

**Discord Username**: {messageAuthor}#{discordDiscrim} `{discordId}`
**Discord Joined date**: <t:{discordJoined}:F>
———————————————————————————————
**MyAnimeList Username**: [{mal_username}](<https://myanimelist.net/profile/{mal_username}>) `{jikanUser['mal_id']}`
**MyAnimeList Joined date**: <t:{joined}:F>"""
                if str(ctx.guild_id) == f'{VERIFICATION_SERVER}':
                    messages += f'''\n
*Now, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={clubId}>) to get your role!*'''
                saveToDatabase(discordId, f'{messageAuthor}#{discordDiscrim}', discordJoined,
                               mal_username, jikanUser['mal_id'], joined, registered, int(ctx.guild_id), discordId)
            except Exception as e:
                messages = returnException(e)

        await ctx.send(messages)


@bot.command(
    name="verify",
    description="Verify your MAL profile to this server!",
    # type=interactions.InteractionType.PING
    scope=[
        int(VERIFICATION_SERVER)
    ]
)
async def verify(ctx: interactions.CommandContext):
    # get the message author username
    messageAuthor = ctx.user
    # get the message author id
    discordId = str(messageAuthor.id)
    # get user joined date
    discordJoined = snowflake_to_datetime(discordId)
    discordJoined = int(discordJoined)
    getMemberDetail = await ctx.guild.get_member(discordId)
    memberRoles = getMemberDetail.roles
    verifiedRole = VERIFIED_ROLE

    clubId = grabClubId(ctx.guild_id)

    if str(ctx.guild_id) != f"{VERIFICATION_SERVER}":
        messages = f"""{EMOJI_USER_ERROR} **You are not allowed to use this command!**
This command only allowed to be used on that particular server.... if you know who's the bot owner is"""
    # check if user is already obtained role
    elif int(verifiedRole) in memberRoles:
        messages = f"""{EMOJI_USER_ERROR} **You are already verified!**"""
    else:
        # check if user is already registered
        if checkIfRegistered(discordId):
            # Grab user's MAL username from database
            with open(database, "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if row[0] == discordId:
                        username = row[3]
                        break
            # Check club membership
            clubs = await checkClubMembership(username)
            for club in clubs:
                if club['mal_id'] == CLUB_ID:
                    await ctx.member.add_role(verifiedRole)
                    messages = f"""{EMOJI_ATTENTIVE} **You have been verified!**"""
                    # exit the loop
                    break
            else:
                messages = f"""{EMOJI_USER_ERROR} **You are not in the club!**
Please join [our club](<https://myanimelist.net/clubs.php?cid={clubId}>) to get your role!"""
        else:
            messages = f"""{EMOJI_DOUBTING} **You are not registered!**
Please use the command `/register` to register your MAL profile to this server!"""

    await ctx.send(messages)


@bot.command(
    name="whois",
    description="Get user's data!",
    # type=interactions.InteractionType.PING,
    options=[
        interactions.Option(
            name="user",
            description="The user to get data from",
            type=interactions.OptionType.USER,
            required=True
        )
    ]
)
async def whois(ctx: interactions.CommandContext, user: int):
    if checkIfRegistered(user.id):
        with open(database, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if row[0] == user.id:
                    # escape markdown
                    row[1] = row[1].replace("*", "\*").replace("_", "\_").replace("~", "\~").replace("`", "\`").replace(
                        "|", "\|").replace(">", "\>").replace("<", "\<").replace("@", "\@").replace("#", "\#").replace(":", "\:")
                    row[3] = row[3].replace("_", "\_")
                    messages = f"""**Discord Username**: {row[1]} `{row[0]}`
**Discord Joined date**: <t:{row[2]}:F>
**Registered date**: <t:{row[6]}:F>
**Registered in**: `{row[7]}` (server ID)"""
                    if row[8] != user.id:
                        messages += f'''
**Registered by**: <@!{row[8]}>'''
                    messages += f"""
———————————————————————————————
**MyAnimeList Username**: {row[3]} ([profile](<https://myanimelist.net/profile/{row[3]}>) | [animelist](<https://myanimelist.net/animelist/{row[3]}>) | [mangalist](<https://myanimelist.net/mangalist/{row[3]}>)) `{row[4]}`
**MyAnimeList Joined date**: <t:{row[5]}:F>"""
                    break

    else:
        messages = f"""{user.name} data is not registered, trying to get only Discord data...
**Discord Username**: {user.name}#{user.discriminator}
**Discord Snowflake**: `{user.id}`
**Discord Joined date**: <t:{int(snowflake_to_datetime(user.id))}:F>"""

    sendMessages = messages

    await ctx.send(sendMessages)


@bot.command(
    name="profile",
    description="Get your MAL profile!",
    # type=interactions.InteractionType.PING
    options=[
        interactions.Option(
            name="user",
            description="The user to get data from by looking up",
            type=interactions.OptionType.USER,
            required=False
        ),
        interactions.Option(
            name="mal_username",
            description="The user to get data from using MAL username",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def profile(ctx: interactions.CommandContext, user: int = None, mal_username: str = None):
    async def getDataFromDB(discordId):
        try:
            if checkIfRegistered(discordId):
                with open(database, "r") as f:
                    reader = csv.reader(f, delimiter="\t")
                    for row in reader:
                        if row[0] == discordId:
                            jikanStats = await jikan.users(username=row[3], extension='statistics')
                            malUname = row[3].replace("_", "\_")
                            malAnime = jikanStats['data']['anime']
                            malManga = jikanStats['data']['manga']
                            return f"""<@{discordId}> data:

**MyAnimeList Username**: {malUname} ([profile](<https://myanimelist.net/profile/{malUname}>) | [animelist](<https://myanimelist.net/animelist/{malUname}>) | [mangalist](<https://myanimelist.net/mangalist/{malUname}>))
———————————————————————————————
**Anime Stats**
• Days watched: {malAnime['days_watched']}
• Mean score: {malAnime['mean_score']}
• Total entries: {malAnime['total_entries']}
👀 {malAnime['watching']} | ✅ {malAnime['completed']} | ⏸️ {malAnime['on_hold']} | 🗑️ {malAnime['dropped']} | ⏰ {malAnime['plan_to_watch']}
*Episodes watched: {malAnime['episodes_watched']}*
———————————————————————————————
**Manga Stats**
• Days read: {malManga['days_read']}
• Mean score: {malManga['mean_score']}
• Total entries: {malManga['total_entries']}
👀 {malManga['reading']} | ✅ {malManga['completed']} | ⏸️ {malManga['on_hold']} | 🗑️ {malManga['dropped']} | ⏰ {malManga['plan_to_read']}
*Chapters read: {malManga['chapters_read']}* | *Volumes read: {malManga['volumes_read']}*"""
            else:
                return f"""{EMOJI_DOUBTING} **User is not registered to the bot!**"""
        except Exception as e:
            return returnException(e)

    if user and mal_username:
        sendMessages = f"""{EMOJI_USER_ERROR} **You cannot use both options!**"""
        embed = None
    if (user is None) and (mal_username is None):
        sendMessages = await getDataFromDB(ctx.author.id)
        embed = None
    elif user is not None:
        sendMessages = await getDataFromDB(user.id)
        embed = None
    elif mal_username is not None:
        try:
            jikanStats = await jikan.users(username=mal_username, extension='statistics')
            malUname = mal_username.replace("_", "\_")
            malAnime = jikanStats['data']['anime']
            malManga = jikanStats['data']['manga']
            embed = interactions.Embed().set_image(
                url=f"https://malheatmap.com/users/{malUname}/signature")
            sendMessages = f"""**MyAnimeList Username**: {malUname} ([profile](<https://myanimelist.net/profile/{malUname}>) | [animelist](<https://myanimelist.net/animelist/{malUname}>) | [mangalist](<https://myanimelist.net/mangalist/{malUname}>))
———————————————————————————————
**Anime Stats**
• Days watched: {malAnime['days_watched']}
• Mean score: {malAnime['mean_score']}
• Total entries: {malAnime['total_entries']}
👀 {malAnime['watching']} | ✅ {malAnime['completed']} | ⏸️ {malAnime['on_hold']} | 🗑️ {malAnime['dropped']} | ⏰ {malAnime['plan_to_watch']}
*Episodes watched: {malAnime['episodes_watched']}*
———————————————————————————————
**Manga Stats**
• Days read: {malManga['days_read']}
• Mean score: {malManga['mean_score']}
• Total entries: {malManga['total_entries']}
👀 {malManga['reading']} | ✅ {malManga['completed']} | ⏸️ {malManga['on_hold']} | 🗑️ {malManga['dropped']} | ⏰ {malManga['plan_to_read']}
*Chapters read: {malManga['chapters_read']}* | *Volumes read: {malManga['volumes_read']}*"""
        except Exception as e:
            sendMessages = returnException(e)
            embed = None

    await ctx.send(content=sendMessages, embeds=embed)


@bot.command(
    name="unregister",
    description="Unregister your MAL account from the bot!",
)
async def unregister(ctx: interactions.CommandContext):
    if checkIfRegistered(ctx.author.id):
        # use pandas to read and drop the row
        try:
            df = pd.read_csv(database, sep="\t")
            df_drop = df.drop(df.query(f"discordId=={ctx.author.id}").index)
            df_drop.to_csv(database, sep="\t", index=False, encoding='utf-8')
            sendMessages = f"""{EMOJI_SUCCESS} **Successfully unregistered!**"""
        except Exception as e:
            sendMessages = returnException(e)
    else:
        sendMessages = f"""{EMOJI_USER_ERROR} **You are not registered!**"""

    await ctx.send(sendMessages)


@bot.command(
    name="about",
    description="Show information about this bot!"
)
async def about(ctx: interactions.CommandContext):
    ownerUserUrl = f'https://discord.com/users/{AUTHOR_USERID}'
    messages = f'''<@!{BOT_CLIENT_ID}> is a bot personally created and used by [nattadasu](<https://nattadasu.my.id>) as member verification and MAL profile integration bot, which is distributed under [AGPL 3.0](<https://www.gnu.org/licenses/agpl-3.0.en.html>) license. ([Source Code](<https://github.com/nattadasu/ryuuRyuusei>)

This bot may requires your consent to collect and store your data when you invoke `/register` command. You can see the privacy policy by using `/privacy` command.

However, you still able to use the bot without collecting your data, albeit limited usage.

If you want to contact the author, send a DM to [{AUTHOR_USERNAME}](<{ownerUserUrl}>) or via [support server](<{BOT_SUPPORT_SERVER}>).
'''
    await ctx.send(messages)


@bot.command(
    name="privacy",
    description="Read privacy policy of this bot, especially for EU (GDPR) and California (CPRA/CCPA) users!"
)
async def privacy(ctx: interactions.CommandContext):
    messages = '''Hello and thank you for your interest to read this tl;dr version of Privacy Policy.

In this message we shortly briefing which content we collect, store, and use, including what third party services we used for bot to function as expected.

__We collect, store, and use following data__:
- MyAnimeList: username, user ID, joined date
- Discord: username, discriminator, user ID, joined date, guild/server ID of registration, date of registration, user referral (if any)

__We do not collect, however, following data__:
- Logs of messages sent by system. Logging only will be enabled during development, testing, or maintenance.

Data stored locally to Data Maintainer's (read: owner) server/machine of this bot. To read your profile that we've collected, type `/export_data` following your username.

__We used following modules/technology for the bot__:
- [Discord](<https://discord.com>), through [Python: `interactions.py`](<https://github.com/interactions-py/interactions.py>).
- [MyAnimeList](<https://myanimelist.net>), through [Jikan](<https://jikan.moe/>) (Python: `jikanpy`) and [MAL Heatmap](<https://malheatmap.com>).
- ✨ [nattadasu's AnimeApi Relation](<https://aniapi.nattadasu.my.id>).
- ✨ [nattadasu's nekomimiDb](<https://github.com/nattadasu/nekomimiDb>).

As user, you have right to create a profile by typing `/register` and accept privacy consent and/or modify/delete your data by typing `/unregister`.

For any contact information, type `/about`.

✨: No data is being transmitted than bot's IP address.'''

    await ctx.send(messages)


@bot.command(
    name="export_data",
    description="Export your data from the bot, made for GDPR, CPRA, LGDP users!",
)
async def export_data(ctx: interactions.CommandContext):
    userId = ctx.author.id
    if checkIfRegistered(userId):
        with open(database, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if row[0] == 'discordId':
                    header = row
                    continue
                if row[0] == str(userId):
                    row[0] = int(row[0])
                    row[2] = int(row[2])
                    row[4] = int(row[4])
                    row[5] = int(row[5])
                    row[6] = int(row[6])
                    row[7] = int(row[7])
                    row[8] = int(row[8])
                    userRow = row
                    userRow = dict(zip(header, userRow))
                    userRow = json.dumps(userRow)
                    messages = f"""{EMOJI_SUCCESS} **Here's your data!**
```json
{userRow}
```or, do you prefer Python list format?```python
{{{header},
{row}}}```"""
                    break
    else:
        messages = f"""{EMOJI_USER_ERROR} **You are not registered!**"""

    await ctx.send(messages)


@bot.command(
    name="heatmap",
    description="Get your MAL Heatmap! Recommended to use after init in the website.",
    # type=interactions.InteractionType.PING
    options=[
        interactions.Option(
            name="user",
            description="The user to get data from by looking up",
            type=interactions.OptionType.USER,
            required=False
        ),
        interactions.Option(
            name="mal_username",
            description="The user to get data from using MAL username",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def heatmap(ctx: interactions.CommandContext, user: int = None, mal_username: str = None):
    async def getDataFromDB(discordId):
        try:
            if checkIfRegistered(discordId):
                with open(database, "r") as f:
                    reader = csv.reader(f, delimiter="\t")
                    for row in reader:
                        if row[0] == discordId:
                            malUname = row[3]
                            return f"""https://malheatmap.com/users/{malUname}/signature"""
            else:
                return f"""{EMOJI_DOUBTING} **User is not registered to the bot!**"""
        except Exception as e:
            return returnException(e)

    if user and mal_username:
        sendMessages = f"""{EMOJI_USER_ERROR} **You cannot use both options!**"""
    if (user is None) and (mal_username is None):
        sendMessages = await getDataFromDB(ctx.author.id)
    elif user is not None:
        sendMessages = await getDataFromDB(user.id)
    elif mal_username is not None:
        try:
            malUname = mal_username
            # embed = interactions.Embed().set_image(url=f"https://malheatmap.com/users/{malUname}/signature")
            sendMessages = f"""https://malheatmap.com/users/{malUname}/signature"""
        except Exception as e:
            sendMessages = returnException(e)

    await ctx.send(content=sendMessages)


@bot.command(
    name="admin_register",
    description="Register user to the bot, for admin only!",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="dc_username",
            description="The user to register",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.Option(
            name="mal_username",
            description="The user's MAL username",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def admin_register(ctx: interactions.CommandContext, dc_username: int, mal_username: str):
    discordId = dc_username.id
    discordUsername = dc_username.username
    discordDiscriminator = dc_username.discriminator
    discordJoined = int(snowflake_to_datetime(dc_username.id))
    malUname = mal_username
    try:
        if checkIfRegistered(discordId):
            sendMessages = f"""{EMOJI_DOUBTING} **User is already registered!**"""
        else:
            jikanData = await getJikanData(malUname)
            malUid = jikanData['mal_id']
            malJoined = int(datetime.datetime.strptime(
                jikanData['joined'], "%Y-%m-%dT%H:%M:%S+00:00").timestamp())
            registeredAt = int(datetime.datetime.now().timestamp())
            registeredGuild = ctx.guild_id
            registeredBy = ctx.author.id
            sendMessages = f"""{EMOJI_SUCCESS} **User registered!**```json
{{
    "discordId": {discordId},
    "discordUsername": "{discordUsername}#{discordDiscriminator}",
    "discordJoined": {discordJoined},
    "malUname": "{malUname}",
    "malId": {malUid},
    "malJoined": {malJoined},
    "registeredAt": {registeredAt},
    "registeredGuild": {registeredGuild},
    "registeredBy": {registeredBy}
}}```"""
            saveToDatabase(discordId, f'{discordUsername}#{discordDiscriminator}', discordJoined, str(
                malUname), malUid, malJoined, registeredAt, registeredGuild, registeredBy)
    except Exception as e:
        sendMessages = returnException(e)

    await ctx.send(sendMessages)


@bot.command(
    name="admin_unregister",
    description="Unregister user from the bot, for admin only!",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="dc_username",
            description="The user to unregister",
            type=interactions.OptionType.USER,
            required=True
        )
    ]
)
async def admin_unregister(ctx: interactions.CommandContext, dc_username: int):
    discordId = dc_username.id
    if checkIfRegistered(discordId):
        try:
            df = pd.read_csv(database, sep="\t")
            df_drop = df.drop(df.query(f'discordId == {discordId}').index)
            df_drop.to_csv(database, sep="\t", index=False, encoding="utf-8")
            sendMessages = f"""{EMOJI_SUCCESS} **User unregistered!**"""
        except Exception as e:
            sendMessages = returnException(e)
    else:
        sendMessages = f"""{EMOJI_DOUBTING} **User is not registered!**"""

    await ctx.send(sendMessages)


@bot.command(
    name="anime",
    description="Get anime information from MAL and AniAPI",
    options=[
        interactions.Option(
            name="anime_name",
            description="The anime name to search",
            type=interactions.OptionType.STRING,
            required=False
        ),
        interactions.Option(
            name="mal_id",
            description="The anime MAL ID to get, if anime_name cannot fetch the data",
            type=interactions.OptionType.INTEGER,
            required=False
        )
    ]
)
async def anime(ctx: interactions.CommandContext, anime_name: str = None, mal_id: int = None):
    async def lookupByNameAniList(aniname: str):
        rawData = await searchAniList(name=aniname)
        return rawData[0]['idMal']
        # romaji = ani['title']['romaji']
        # english = ani['title']['english']
        # native = ani['title']['native']
        # syns = ani['synonyms']
        # myAnimeListID = ani['idMal']
        # if (romaji == name) or (english == name) or (native == name):
        #     return myAnimeListID
        # else:
        #     for title in syns:
        #         if title == name:
        #             return myAnimeListID
        # return myAnimeListID

    async def lookupByNameJikan(name: str):
        rawData = await searchJikanAnime(name)
        for ani in rawData:
            romaji = ani['title']
            english = ani['title_english']
            native = ani['title_japanese']
            syns = ani['titles']
            myAnimeListID = ani['mal_id']
            if (romaji == name) or (english == name) or (native == name):
                return myAnimeListID
            else:
                for title in syns:
                    if title == name:
                        return myAnimeListID

    async def lookupById(entry_id: int, guild_id: int = ctx.guild_id):
        j = await getJikanAnime(entry_id)
        if str(guild_id) == '449172244724449290':
            for g in j['genres']:
                gn = g['name']
                if "Hentai" in gn:
                    raise Exception(
                        f"""{EMOJI_FORBIDDEN} **Hentai is not allowed!**""")
                # elif "Boys Love" in gn:
                #     raise Exception(f"""{EMOJI_FORBIDDEN} **Boys' Love is not allowed!**""")
                # elif "Girls Love" in gn:
                #     raise Exception(f"""{EMOJI_FORBIDDEN} **Girls' Love is not allowed!**""")
        m = j['mal_id']
        aa = await getNatsuAniApi(m, platform="myanimelist")
        aniApi = aa
        # s = await getSimklFromMal(m)
        # sm = await getSimklAnime(s)
        # simkl = sm
        # simklId = s
        # tr = await getTraktFromTMDB(sm['ids']['tmdb'])
        # trakt = tr
        if j['synopsis'] is not None:
            j_spl = j['synopsis'].split("\n")
            synl = len(j_spl)
            cyno = j_spl[0]
            # trim synopsys if too long for discord, max 600 chars
            if len(str(cyno)) > 600:
                cyno = cyno[:600]
                cyno += "..."
            if synl > 0:
                cyno += f"\n> \n> *Read more on [MyAnimeList](<https://myanimelist.net/anime/{m}>)...*"
        else:
            cyno = "*None*"

        pdta = f"[MyAnimeList](<https://myanimelist.net/anime/{m}>)"
        if aa['aniDb'] is not None:
            pdta += f" | [aniDB](<https://anidb.net/anime/{aa['aniDb']}>)"
        if aa['aniList'] is not None:
            pdta += f" | [AniList](<https://anilist.co/anime/{aa['aniList']}>)"
        if aniApi['aniSearch'] is not None:
            pdta += f" | [aniSearch](<https://anisearch.com/anime/{aniApi['aniSearch']}>)"
        # if simkl['ids']['imdb'] is not None:
        #     pdta += f" | [IMDb](<https://www.imdb.com/title/{simkl['ids']['imdb']}>)"
        if aniApi['kaize'] is not None:
            pdta += f" | [Kaize](<https://kaize.io/anime/{aniApi['kaize']}>)"
        if aniApi['kitsu'] is not None:
            pdta += f" | [Kitsu](<https://kitsu.io/anime/{aniApi['kitsu']}>)"
            poster = f"https://media.kitsu.io/anime/poster_images/{aniApi['kitsu']}/small.jpg"
        if aniApi['liveChart'] is not None:
            pdta += f" | [LiveChart](<https://livechart.me/anime/{aniApi['liveChart']}>)"
        if aniApi['myAnimeList'] is not None:
            poster = j['images']['jpg']['image_url']
        if aniApi['notifyMoe'] is not None:
            pdta += f" | [Notify](<https://notify.moe/anime/{aniApi['notifyMoe']}>)"
        # if simklId is not None:
        #     pdta += f" | [SIMKL](<https://simkl.com/anime/{simklId}>)"
        if aniApi['myAnimeList'] is not None:
            pdta += f" | [Шикимори](<https://shikimori.one/animes/{m}>)"
        # if simkl['ids']['tmdb'] is not None:
        #     pdta += f" | [TMDB](<https://www.themoviedb.org/tv/{simkl['ids']['tmdb']}>)"
        # if trakt is not None:
        #     pdta += f" | [Trakt](<https://trakt.tv/shows/{trakt['ids']['slug']}>)"
        # if simkl['ids']['tvdbslug'] is not None:
        #     pdta += f" | [TVDB](<https://www.thetvdb.com/series/{simkl['ids']['tvdbslug']}>)"

        # Build sendMessages
        tgs = []
        for g in j["genres"]:
            gn = g["name"]
            gu = g["url"]
            tgs += [f"[{gn}](<{gu}>)"]
        for g in j["themes"]:
            gn = g["name"]
            gu = g["url"]
            tgs += [f"[{gn}](<{gu}>)"]
        # sort tgs alphabetically ascending
        tgs = tgs.sort()
        tgs = ", ".join(tgs)
        ast = j['aired']['from']
        aen = j['aired']['to']
        if ast is not None:
            ast = int(datetime.datetime.strptime(
                ast, '%Y-%m-%dT00:00:00+00:00').timestamp())
        else:
            ast = 0

        if aen is not None:
            aen = int(datetime.datetime.strptime(
                aen, '%Y-%m-%dT00:00:00+00:00').timestamp())
        else:
            aen = 0

        # # create a synonyms list
        # syns = []
        # for s in j['titles']:
        #     syns += [j['title']]
        # ogt = [j['title_english'], j['title_japanese'], j['title']]
        # syns = [x for x in syns if x not in ogt]
        # syns = list(dict.fromkeys(syns))
        # if ogt in syns:
        #     # Remove duplicates if in synonyms includes title_english and title_japanese
        #     syns.remove(ogt)

        # if len(syns) > 5:
        #     syns = syns[:5]
        #     syns = ", ".join(syns)

        # format people voted for to be more readable (1,000 instead of 1000)
        pvd = j['scored_by']
        if j['scored_by'] > 1:
            pvd = f"{j['scored_by']:,} people voted"

        return f'''**[{j['title']}](<https://myanimelist.net/anime/{m}>)** `{m}` ({j['type']}, {j['season']} {j['year']}, ⭐ {j['score']}/10 by {pvd}) [🖼️]({poster})
{pdta}

**Synopsis**
> {cyno}

**English Title**: {j['title_english']}
**Native Title**: {j['title_japanese']}
**Genres and Themes**: {tgs}
**Episodes**: {j['episodes']}/{j['duration']} ({j['status']})
**Aired**: <t:{ast}:D> - <t:{aen}:D> (<t:{ast}:R>)
'''

    if anime_name is None and mal_id is None:
        sendMessages = f"""{EMOJI_USER_ERROR} **Please provide anime name or MAL ID!**"""
    elif (anime_name is not None) and (mal_id is not None):
        sendMessages = f"""{EMOJI_USER_ERROR} **You can not use both `anime_name` and `mal_id`!**"""
    else:
        ani_id = mal_id
        if (ani_id is None) or (ani_id == 0):
            ani_id = await lookupByNameAniList(anime_name)

        if (ani_id is None) or (ani_id == 0):
            ani_id = await lookupByNameJikan(anime_name)

        if ani_id is not None:
            sendMessages = await lookupById(ani_id)
        else:
            sendMessages = returnException("no anime found")

    await ctx.send(sendMessages)


@bot.command(
    name="random_nekomimi",
    description="Get a random image of characters with cat ears, powered by Natsu's nekomimiDb!",
    options=[
        interactions.Option(
            name="bois",
            description="Show cat boys instead?",
            type=interactions.OptionType.BOOLEAN,
            required=True
        )
    ]
)
async def random_nekomimi(ctx: interactions.CommandContext, bois: bool):
    # open the csv from nekomimiDb.tsv using pandas
    nmDb = pd.read_csv("nekomimiDb.tsv", sep="\t")
    # assumes the header as such:
    # id	imageUrl	artist	artistUrl	platform	imageSourceUrl	mediaSource	girlOrBoy
    if bois is True:
        # do a query to grab images if girlOrBoy is 'boy'
        query = nmDb[nmDb['girlOrBoy'] == 'boy']
    else:
        query = nmDb[nmDb['girlOrBoy'] == 'girl']
    # get a random row from the query
    row = query.sample()
    # get the image url
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]

    # Send the image url to the user
    await ctx.send(f"[🖼️]({str(img)}) **{mediaSource}** by [{artist}](<{artistUrl}>) | [Image source](<{imageSourceUrl}>)")

@bot.command(
    name="invite",
    description="Invite me to your server!"
)
async def invite(ctx: interactions.CommandContext):
    sendMessages = f"""{EMOJI_ATTENTIVE} Thanks for your interest in inviting me to your server!

You can invite me by [clicking/pressing here](<https://discord.com/api/oauth2/authorize?client_id={BOT_CLIENT_ID}&permissions=8&scope=bot%20applications.commands>).

For more information, we need `Administrator` access, and scope used are `bot` and `applications.commands`.

If you have any questions, please join my [support server]({BOT_SUPPORT_SERVER})!"""
    await ctx.send(sendMessages)

print("Starting bot...")

async def downloadNekomimiDB():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://raw.githubusercontent.com/nattadasu/nekomimiDb/main/index.tsv") as resp:
            if resp.status == 200:
                print("Downloading nekomimiDB...")
                with open("nekomimiDb.tsv", "wb") as f:
                    f.write(await resp.read())
                print("Downloaded nekomimiDB!")
            else:
                print("Failed to download nekomimiDB!")
                print(f"Status code: {resp.status}")

bot.start()
