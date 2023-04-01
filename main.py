#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cspell:disable

from modules.commons import *

from modules.anilist import *
from modules.animeapi import *
from modules.database import *
from modules.kitsu import *
from modules.myanimelist import *
from modules.nekomimidb import *
from modules.rawg import *
from modules.platforms import *
from modules.simkl import *
from modules.trakt import *


gittyHash = get_git_revision_hash()
gtHsh = get_git_revision_short_hash()


bot = interactions.Client(
    token=BOT_TOKEN,
    presence=interactions.ClientPresence(
        since=None,
        activities=[
            interactions.PresenceActivity(
                name="Kagamine Len's concert",
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

# START OF BOT CODE

@bot.command(
    name="ping",
    description="Ping the bot!"
)
async def ping(ctx: interactions.CommandContext):
    # create a time var when the command invoked
    start = time.perf_counter()
    await ctx.defer()  # to make sure if benchmark reflects other commands with .defer()
    # send a message to the channel
    await ctx.send(f"{EMOJI_ATTENTIVE} Pong!")
    # get the time when the message was sent
    end = time.perf_counter()
    # calculate the time it took to send the message
    duration = (end - start) * 1000
    # if durations is above 1000ms, show additional message
    if duration > 2500:
        msg = f"{EMOJI_FORBIDDEN} Whoa, that's so slow! Please contact the bot owner!"
    elif duration > 1000:
        msg = f"{EMOJI_DOUBTING} That's slow! But don't worry, it's still working!"
    else:
        msg = f"{EMOJI_SUCCESS} I'm working as intended!"
    # send a message to the channel
    await ctx.edit(f"{EMOJI_ATTENTIVE} Pong! Response time: {duration:.2f}ms\n{msg}")


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
    await ctx.defer(ephemeral=True)
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
        await ctx.send(messages, ephemeral=True)
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
        discordServerName = ctx.guild.name

        clubId = CLUB_ID

        # check if user is already registered
        if checkIfRegistered(discordId):
            messages = f"""{EMOJI_DOUBTING} **You are already registered!**"""
            if str(ctx.guild_id) == f'{VERIFICATION_SERVER}':
                messages += f'''\nTo get your role back, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={clubId}>)!'''
        else:
            # get user id from jikan
            try:
                uname = mal_username.strip()
                jikanUser = await getJikanData(uname)
                uname = jikanUser['username']
                # convert joined date to epoch
                jikanUser['joined'] = jikanUser['joined'].replace(
                    "+00:00", "+0000")
                joined = datetime.datetime.strptime(
                    jikanUser['joined'], "%Y-%m-%dT%H:%M:%S%z")
                joined = joined.timestamp()
                # try remove decimal places from joined
                joined = int(joined)
                registered = datetime.datetime.now().timestamp()
                registered = int(registered)
                messages = f"""{EMOJI_SUCCESS} **Your account has been registered!** :tada:

**Discord Username**: {messageAuthor}#{discordDiscrim} `{discordId}`
**Discord Joined date**: <t:{discordJoined}:F>
———————————————————————————————
**MyAnimeList Username**: [{uname}](<https://myanimelist.net/profile/{uname}>) `{jikanUser['mal_id']}`
**MyAnimeList Joined date**: <t:{joined}:F>"""
                if str(ctx.guild_id) == f'{VERIFICATION_SERVER}':
                    messages += f'''\n
*Now, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={clubId}>) to get your role!*'''
                saveToDatabase(discordId, f'{messageAuthor}#{discordDiscrim}', discordJoined,
                               uname, jikanUser['mal_id'], joined, registered, int(ctx.guild_id), discordId, discordServerName)
            except Exception as e:
                messages = returnException(e)

        await ctx.send(messages, ephemeral=True)


@bot.command(
    name="verify",
    description="Verify your MAL profile to this server!",
    # type=interactions.InteractionType.PING
    scope=[
        int(VERIFICATION_SERVER)
    ]
)
async def verify(ctx: interactions.CommandContext):
    await ctx.defer()
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

    if str(ctx.guild_id) != f"{VERIFICATION_SERVER}":
        messages = f"""{EMOJI_USER_ERROR} **You are not allowed to use this command!**
This command only allowed to be used on that particular server.... if you know who's the bot owner is"""
    # check if user is already obtained role
    elif int(verifiedRole) in memberRoles:
        messages = f"""{EMOJI_USER_ERROR} **You are already verified!**"""
    else:
        # check if user is already registered
        if checkIfRegistered(discordId):
            verified = await verifyUser(discordId=discordId)
            if verified is True:
                await ctx.member.add_role(verifiedRole, reason="Verified by bot")
                messages = f"""{EMOJI_ATTENTIVE} **You have been verified!**"""
            elif verified is False:
                messages = f"""{EMOJI_USER_ERROR} **You are not in the club!**
Please join [our club](<https://myanimelist.net/clubs.php?cid={CLUB_ID}>) to get your role!"""
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
    await ctx.defer()

    try:
        if checkIfRegistered(user.id):
            row = []
            with open(database, "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if row[0] == user.id:
                        # escape markdown
                        row[1] = sanitizeMarkdown(row[1])
                        row[3] = row[3].replace("_", "\\_")
                        if row[8] != user.id:
                            assistedRegister = f"\nRegistered by: <@!{row[8]}>"
                        else:
                            assistedRegister = ""
                        row = row
                        break
            userData = await getUserData(user_snowflake=row[0])
            userJoined = await getGuildMemberData(guild_snowflake=ctx.guild_id, user_snowflake=row[0])
            userJoined = datetime.datetime.strptime(
                userJoined['joined_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
            userJoined = int(userJoined.timestamp())
            userAvatar: str = userData['avatar']
            # check if avatar has a_ prefix
            if userAvatar.startswith("a_"):
                fileExt = "gif"
            else:
                fileExt = "webp"
            userBanner: str = userData['banner']
            userDecColor = userData['accent_color']
            messages = ""
            dcEm = interactions.Embed(
                title=f"{user.username}#{user.discriminator} data",
                thumbnail=interactions.EmbedImageStruct(
                    url=f"https://cdn.discordapp.com/avatars/{user.id}/{userAvatar}.{fileExt}?size=512"
                ),
                color=userDecColor,
                fields=[
                    interactions.EmbedField(
                        name="Discord",
                        value=f"""Username: {row[1]}
Snowflake: `{row[0]}`
Created date: <t:{row[2]}:F>
Joined to {ctx.guild.name}: <t:{userJoined}:F>""",
                    ),
                    interactions.EmbedField(
                        name="Bot Database",
                        value=f"""Registered date: <t:{row[6]}:F>
Registered in: {row[9]}
Server Snowflake: `{row[7]}`{assistedRegister}"""
                    ),
                    interactions.EmbedField(
                        name="MyAnimeList",
                        value=f"""Username: [{row[3]}](<https://myanimelist.net/profile/{row[3]}>) ([Anime List](<https://myanimelist.net/animelist/{row[3]}>) | [Manga List](<https://myanimelist.net/mangalist/{row[3]}>))
User ID: `{row[4]}`
Created date: <t:{row[5]}:F>"""
                    )
                ],
                image=interactions.EmbedImageStruct(
                    url=f"https://cdn.discordapp.com/banners/{row[0]}/{userBanner}.webp?size=512"
                )
            )

        else:
            messages = f"<@!{user.id}> data is not registered, trying to get only Discord data..."
            userData = await getUserData(user_snowflake=user.id)
            userJoined = await getGuildMemberData(guild_snowflake=ctx.guild_id, user_snowflake=user.id)
            userJoined = datetime.datetime.strptime(
                userJoined['joined_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
            userJoined = int(userJoined.timestamp())
            userAvatar: str = userData['avatar']
            # check if avatar has a_ prefix
            if userAvatar.startswith("a_"):
                fileExt = "gif"
            else:
                fileExt = "webp"
            userBanner: str = userData['banner']
            userDecColor = userData['accent_color']
            dcEm = interactions.Embed(
                title=f"{user.username}#{user.discriminator} data",
                color=userDecColor,
                fields=[
                    interactions.EmbedField(
                        name="Discord",
                        value=f"""Username: {user.username}#{user.discriminator}
Snowflake: `{user.id}`
Created date: <t:{int(snowflake_to_datetime(user.id))}:F>
Joined to {ctx.guild.name}: <t:{userJoined}:F>"""
                    )
                ],
                thumbnail=interactions.EmbedImageStruct(
                    url=f"https://cdn.discordapp.com/avatars/{user.id}/{userAvatar}.{fileExt}?size=512"
                ),
                image=interactions.EmbedImageStruct(
                    url=f"https://cdn.discordapp.com/banners/{user.id}/{userBanner}.webp?size=512"
                )
            )

        sendMessages = messages
    except AttributeError:
        sendMessages = ""
        dcEm = interactions.Embed(
            color=0xff0000,
            title="Error",
            description=returnException(
                "User can not be found if they're joined this server or not.")
        )
    except Exception as e:
        sendMessages = ""
        dcEm = exceptionsToEmbed(returnException(e))

    await ctx.send(sendMessages, embeds=dcEm)


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
        ),
        interactions.Option(
            name="extended",
            description="Extend embed result, show your anime/manga stats and useful links",
            type=interactions.OptionType.BOOLEAN,
            required=False
        )
    ]
)
async def profile(ctx: interactions.CommandContext, user: int = None, mal_username: str = None, extended: bool = False):
    await ctx.defer()

    userRegistered = f"{EMOJI_DOUBTING} **You are looking at your own profile!**\nYou can also use </profile:1072608801334755529> without any arguments to get your own profile!"

    if (user is not None) and (mal_username is not None):
        try:
            raise KeyError
        except KeyError:
            sendMessages = ""
            dcEm = interactions.Embed(
                title="Error",
                description=returnException(
                    f"{EMOJI_USER_ERROR} **You cannot use both options!** Use either one of `user:` or `mal_username:`, hmph. >:("),
                color=0xFF0000
            )
    else:
        if mal_username is None:
            if user is not None:
                uid = user.id
            else:
                uid = ctx.author.id
            try:
                if checkIfRegistered(uid):
                    with open(database, "r") as f:
                        reader = csv.reader(f, delimiter="\t")
                        for row in reader:
                            if row[0] == uid:
                                jikanStats = await jikan.users(username=row[3], extension='full')
                                break
                    malProfile = jikanStats['data']
                    mun = malProfile['username'].replace("_", "\\_")
                    mid = malProfile['mal_id']
                    ani = malProfile['statistics']['anime']
                    man = malProfile['statistics']['manga']
                    bth = None
                    if malProfile['birthday'] is not None:
                        bth = malProfile['birthday'].replace(
                            "+00:00", "+0000")
                        bth = int(datetime.datetime.strptime(
                            bth, "%Y-%m-%dT%H:%M:%S%z").timestamp())
                    dtJoin = malProfile['joined'].replace(
                        "+00:00", "+0000")
                    dtJoin = int(datetime.datetime.strptime(
                        dtJoin, "%Y-%m-%dT%H:%M:%S%z").timestamp())

                    dcEm = generateProfile(uname=mun, uid=mid, malAnime=ani, malManga=man, joined=dtJoin, bday=bth, extend=extended)
                    if user is None:
                        sendMessages = ""
                    elif ctx.author.id == uid:
                        sendMessages = userRegistered
                    else:
                        sendMessages = f"<@{uid}> data:"
                else:
                    if user is None:
                        raise KeyError(
                            f"{EMOJI_USER_ERROR} Sorry, but to use standalone command, you need to `/register` your account. Or, you can use `/profile mal_username:<yourUsername>` instead")
                    else:
                        raise KeyError(
                            f"I couldn't find <@!{uid}> on my database. It could be that they have not registered their MAL account yet.")
            except KeyError as regAccount:
                foo = "Please be a good child, okay? 🚶‍♂️" if user is None else ""
                sendMessages = ""
                dcEm = interactions.Embed(
                    title="User have not registered yet!",
                    description=returnException(regAccount),
                    color=0xFF0000,
                    footer=interactions.EmbedFooter(
                        text=foo
                    )
                )
            except Exception as e:
                sendMessages = ""
                dcEm = definejikanException(e)
        elif mal_username is not None:
            uname = mal_username.strip()
            try:
                with open(database, "r") as f:
                    reader = csv.reader(f, delimiter="\t")
                    for row in reader:
                        if (str(row[3]).lower() == str(uname).lower()) and (ctx.author.id == row[0]):
                            sendMessages = userRegistered
                            break
                        elif (str(row[3]).lower() == str(uname).lower()) and (ctx.author.id != row[0]):
                            sendMessages = f"{EMOJI_ATTENTIVE} This MAL account is registered on this bot, you could use `/profile user:<@!{row[0]}>` instead"
                            break
                        else:
                            sendMessages = ""
                jikanStats = await jikan.users(username=uname, extension='full')
                malProfile = jikanStats['data']
                mun = malProfile['username'].replace("_", "\\_")
                mid = malProfile['mal_id']
                ani = malProfile['statistics']['anime']
                man = malProfile['statistics']['manga']
                bth = None
                if malProfile['birthday'] is not None:
                    bth = malProfile['birthday'].replace("+00:00", "+0000")
                    bth = int(datetime.datetime.strptime(
                        bth, "%Y-%m-%dT%H:%M:%S%z").timestamp())
                dtJoin = malProfile['joined'].replace("+00:00", "+0000")
                dtJoin = int(datetime.datetime.strptime(
                    dtJoin, "%Y-%m-%dT%H:%M:%S%z").timestamp())

                dcEm = generateProfile(uname=mun, uid=mid, malAnime=ani, malManga=man, joined=dtJoin, bday=bth, extend=extended)
            except Exception as e:
                sendMessages = ""
                dcEm = definejikanException(e)

    await ctx.send(sendMessages, embeds=dcEm)


@bot.command(
    name="unregister",
    description="Unregister your MAL account from the bot!",
)
async def unregister(ctx: interactions.CommandContext):
    if checkIfRegistered(ctx.author.id):
        # use pandas to read and drop the row
        try:
            dropUser(discordId=ctx.author.id)
            sendMessages = f"""{EMOJI_SUCCESS} **Successfully unregistered!**"""
        except Exception as e:
            sendMessages = returnException(e)
    else:
        sendMessages = f"""{EMOJI_USER_ERROR} **You are not registered!**"""

    await ctx.send(sendMessages, ephemeral=True)


@bot.command(
    name="about",
    description="Show information about this bot!"
)
async def about(ctx: interactions.CommandContext):
    ownerUserUrl = f'https://discord.com/users/{AUTHOR_USERID}'
    messages = f'''<@!{BOT_CLIENT_ID}> is a bot personally created and used by [nattadasu](<https://nattadasu.my.id>) with the initial purpose as for member verification and MAL profile integration bot, which is distributed under [AGPL 3.0](<https://www.gnu.org/licenses/agpl-3.0.en.html>) license. ([Source Code](<https://github.com/nattadasu/ryuuRyuusei>), source code in repository may be older than main production maintained by nattadasu for)

However, due to how advanced the bot in querying information regarding user, anime on MAL, and manga on AniList, invite link is available for anyone who's interested to invite the bot (see `/invite`).

This bot may requires your consent to collect and store your data when you invoke `/register` command. You can see the privacy policy by using `/privacy` command.

However, you still able to use the bot without collecting your data, albeit limited usage.

If you want to contact the author, send a DM to [{AUTHOR_USERNAME}](<{ownerUserUrl}>) or via [support server](<{BOT_SUPPORT_SERVER}>).

Bot version, in Git hash: [`{gtHsh}`](<https://github.com/nattadasu/ryuuRyuusei/commit/{gittyHash}>)
'''
    await ctx.send(messages)


@bot.command(
    name="privacy",
    description="Read privacy policy of this bot, especially for EU (GDPR) and California (CPRA/CCPA) users!"
)
async def privacy(ctx: interactions.CommandContext):
    messages = '''Hello and thank you for your interest to read this tl;dr version of Privacy Policy.

In this message we shortly briefing which content we collect, store, and use, including what third party services we used for bot to function as expected. You can read the full version of [Privacy Policy here at anytime you wish](<https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md>).

__We collect, store, and use following data__:
- Discord: username, discriminator, user snowflake ID, joined date, guild/server ID of registration, server name, date of registration, user referral (if any)
- MyAnimeList: username, user ID, joined date

__We shared limited personal information about you to 3rd Party__:
This is required for the bot to function as expected, with the following services:
Discord, Last.FM, MAL Heatmap, MyAnimeList

__We cached data for limited features of the bot__:
Used to reduce the amount of API calls to 3rd party services, and to reduce the amount of time to process the data and no information tied to you. This is required for the bot to function as expected, with the following services:
AniList, AnimeAPI, MyAnimeList, SIMKL, The Movie Database (TMDB), Trakt

__We do not collect, however, following data__:
Any logs of messages sent by system about you under any circumstances. Logging of messages only occurs when you invoked general commands (such as `/help`, `/anime`, `/manga`, etc.) and during the bot's development process. Maintenance will announced in the Bot status channel in Support Server and Bot Activity.

Data stored locally to Data Maintainer's (read: owner) server/machine of this bot as CSV. To read your profile that we've collected, type `/export_data` following your username.

As user, you have right to access, know, data portability, modify/rectify, delete, restrict, limit, opt-out, and/or withdraw your consent to use your data.

For any contact information, type `/about`.
'''

    butt = interactions.Button(
        type=2,
        style=interactions.ButtonStyle.LINK,
        label="Read Full Privacy Policy",
        url='https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md'
    )

    await ctx.send(messages, ephemeral=False, components=[butt])


@bot.command(
    name="export_data",
    description="Export your data from the bot, made for GDPR, CPRA, LGDP users!",
)
async def export_data(ctx: interactions.CommandContext):
    await ctx.defer(ephemeral=True)
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
                    row[9] = str(row[9])
                    userRow = dict(zip(header, row))
                    userRow = json.dumps(userRow)
                break
        dcEm = interactions.Embed(
            title="Data Exported!",
            description=f"""{EMOJI_SUCCESS} **Here's your data!**
```json
{userRow}
```or, do you prefer Python List format?```python
[{header},
{row}]```""",
            color=0x2E2E2E,
            footer=interactions.EmbedFooter(
                text="Unregister easily by typing /unregister!"
            )
        )
        messages = None
    else:
        messages = f"""{EMOJI_USER_ERROR} **You are not registered!**"""
        dcEm = None

    await ctx.send(messages, embeds=dcEm, ephemeral=True)


@bot.command(
    name="anime",
    description="Get anime information from MAL and AniAPI"
)
async def anime(ctx: interactions.CommandContext):
    pass


@anime.subcommand()
@interactions.option(
    name="title",
    description="The anime title name to search",
    type=interactions.OptionType.STRING,
    required=True
)
async def search(ctx: interactions.CommandContext, title: str = None):
    """Search anime from MAL by title. Anime lookup powered by AniList"""
    await ctx.defer()
    await ctx.get_channel()

    ani_id = None
    alData = None

    async def lookupByNameAniList(aniname: str) -> dict:
        """Lookup anime by name using AniList"""
        rawData = await searchAniList(name=aniname, isAnime=True)
        return rawData

    async def lookupByNameJikan(name: str) -> dict:
        """Lookup anime by name using Jikan"""
        rawData = await searchJikanAnime(name)
        return rawData

    f = []
    so = []
    com = []
    aniFound = False

    try:
        await ctx.send(f"Searching `{title}` using AniList", embeds=None, components=None)
        alData = await lookupByNameAniList(title)
        if len(alData) == 0 :
            raise Exception()
        else:
            for a in alData:
                f += [
                    interactions.EmbedField(
                        name=f"{a['title']['romaji']}",
                        value=f"""*{a['title']['native']}, {a['format']}, {a['status']}*""",
                        inline=False
                    )
                ]
                so += [
                    interactions.SelectOption(
                        label=f"{a['title']['romaji']}",
                        value=f"{a['idMal']}",
                        description=f"{a['format']}, {a['status']}"
                    )
                ]
            aniFound = True
    except:
        try:
            await ctx.edit(f"AniList failed to search `{title}`, searching via Jikan (inaccurate)", embeds=None, components=None)
            ani = await lookupByNameJikan(title)
            if len(ani) == 0:
                raise Exception()
            else:
                for a in ani:
                    f += [
                        interactions.EmbedField(
                            name=f"{a['title']}",
                            value=f"""*{a['title_japanese']}, {a['type']}, {a['status']}*""",
                            inline=False
                        )
                    ]
                    so += [
                        interactions.SelectOption(
                            label=f"{a['title']}",
                            value=f"{a['mal_id']}",
                            description=f"{a['type']}, {a['status']}"
                        )
                    ]
                aniFound = True
        except:
            aniFound = False

    if aniFound is True:
        try:
            dcEm = interactions.Embed(
                color=0x2F51A3,
                author=interactions.EmbedAuthor(
                    name="MyAnimeList Anime",
                    url="https://myanimelist.net",
                    icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
                ),
                thumbnail=interactions.EmbedImageStruct(
                    url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
                ),
                title="Search Results",
                description=f"Found **{len(f)} results** for `{title}`, please select by choosing right option in the dropdown below",
                fields=f
            )
            com = [
                interactions.SelectMenu(
                    options=so,
                    custom_id="mal_search",
                    placeholder="Select an anime to get more information"
                )
            ]
        except Exception as e:
            dcEm = exceptionsToEmbed(returnException(e))
            com = []
    else:
        dcEm = exceptionsToEmbed(error=f"""We couldn't able to find any anime with that title (`{title}`). Please check the spelling!
**Pro tip**: Use Native title to get most accurate result.... that if you know how to type in such language.""")
        com = []

    await ctx.edit("", embeds=dcEm, components=com)
    if len(com) > 0:
        await asyncio.sleep(90)
        await ctx.edit("*Selection had reached timeout*", embeds=dcEm, components=[])

@bot.component('mal_search')
async def mal_search(ctx: interactions.ComponentContext, choices: list[str]):
    await ctx.defer()
    try:
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        ani_id = int(choices[0])
        aniApi = await getNatsuAniApi(ani_id, platform="myanimelist")
        if aniApi['anilist'] is not None:
            alData = await getAniList(media_id=aniApi['anilist'], isAnime=True)
            if (alData[0]['trailer'] is not None) and (alData[0]['trailer']['site'] == "youtube"):
                trailer = generateTrailer(data=alData[0]['trailer'], isMal=False)
                trailer = [trailer]
            else:
                trailer = []
        dcEm = await generateMal(ani_id, nsfw_bool, alDict=alData, animeApi=aniApi)
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        trailer = []
    await ctx.send("", embeds=dcEm, components=trailer)


@anime.subcommand()
async def random(ctx: interactions.CommandContext):
    """Get random anime information from MAL"""
    await ctx.defer()
    await ctx.get_channel()

    async def lookupRandom() -> int:
        """Lookup random anime from MAL"""
        seed = getRandom()
        # open database/mal.csv
        df = pd.read_csv("database/mal.csv", sep="\t")
        # get random anime
        randomAnime = df.sample(n=1, random_state=seed)
        # get anime id
        randomAnimeId: int = randomAnime['mal_id'].values[0]
        return randomAnimeId

    ani_id = await lookupRandom()
    trailer = None

    await ctx.send(f"Found [`{ani_id}`](<https://myanimelist.net/anime/{ani_id}>), showing information...", ephemeral=True)

    try:
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        sendMessages = None
        aniApi = await getNatsuAniApi(ani_id, platform="myanimelist")
        if aniApi['anilist'] is not None:
            aaDict = await searchAniList(media_id=aniApi['anilist'], isAnime=True)
            if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                trailer = generateTrailer(data=aaDict[0]['trailer'])
        else:
            try:
                aaDict = await searchAniList(name=aniApi['title'], media_id=None, isAnime=True)
                if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                    trailer = generateTrailer(data=aaDict[0]['trailer'])
            except:
                aaDict = None
        dcEm = await generateMal(ani_id, nsfw_bool, aaDict, animeApi=aniApi)
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        sendMessages = ""
        trailer = None

    await ctx.send(sendMessages, embeds=dcEm, components=trailer)


@anime.subcommand()
@interactions.option(
    name="id",
    description="The anime ID on MAL to fetch",
    type=interactions.OptionType.INTEGER,
    required=True
)
async def info(ctx: interactions.CommandContext, id: int):
    """Get anime information from MAL and AniAPI using MAL id"""
    await ctx.defer()
    await ctx.get_channel()
    trailer = None
    try:
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        aniApi = await getNatsuAniApi(id=id, platform='myanimelist')
        if aniApi['anilist'] is not None:
            aaDict = await searchAniList(media_id=aniApi['anilist'], isAnime=True)
            if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                trailer = generateTrailer(data=aaDict[0]['trailer'])
        else:
            try:
                aaDict = await searchAniList(name=aniApi['title'], media_id=None, isAnime=True)
                if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                    trailer = generateTrailer(data=aaDict[0]['trailer'])
            except:
                aaDict = None
        dcEm = await generateMal(id, nsfw_bool, aaDict, animeApi=aniApi)
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        trailer = None

    await ctx.send("", embeds=dcEm, components=trailer)


@anime.subcommand(
    options=[
        interactions.Option(
            name="id",
            description="The anime ID on the platform to search",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="platform",
            description="The platform to search",
            type=interactions.OptionType.STRING,
            choices=[
                interactions.Choice(
                    name="aniDB",
                    value="anidb"
                ),
                interactions.Choice(
                    name="AniList",
                    value="anilist"
                ),
                interactions.Choice(
                    name="Anime-Planet",
                    value="animeplanet"
                ),
                interactions.Choice(
                    name="aniSearch",
                    value="anisearch"
                ),
                interactions.Choice(
                    name="Annict (アニクト)",
                    value="annict"
                ),
                interactions.Choice(
                    name="IMDb",
                    value="imdb"
                ),
                interactions.Choice(
                    name="Kaize",
                    value="kaize"
                ),
                interactions.Choice(
                    name="Kitsu",
                    value="kitsu"
                ),
                interactions.Choice(
                    name="LiveChart",
                    value="livechart"
                ),
                interactions.Choice(
                    name="MyAnimeList",
                    value="myanimelist"
                ),
                interactions.Choice(
                    name="Notify.moe",
                    value="notify"
                ),
                interactions.Choice(
                    name="Otak Otaku",
                    value="otakotaku"
                ),
                interactions.Choice(
                    name="Shikimori (Шикимори)",
                    value="shikimori"
                ),
                interactions.Choice(
                    name="Shoboi Calendar (しょぼいカレンダー)",
                    value="shoboi"
                ),
                interactions.Choice(
                    name="Silver Yasha: DB Tontonan Indonesia",
                    value="silveryasha"
                ),
                interactions.Choice(
                    name="SIMKL",
                    value="simkl"
                ),
                interactions.Choice(
                    name="Trakt*",
                    value="trakt"
                ),
                interactions.Choice(
                    name="The Movie Database",
                    value="tmdb"
                ),
                interactions.Choice(
                    name="The TVDB",
                    value="tvdb"
                )
            ],
            required=True
        )
    ]
)
async def relations(ctx: interactions.CommandContext, id: str, platform: str):
    """Find a list of relations to external site for an anime"""
    await ctx.defer()
    await ctx.send(f"Searching for relations on `{platform}` using ID: `{id}`", embeds=None)
    try:
        simId = 0
        imdbId = None
        malId = None
        tmdbId = None
        traktId = None
        trkSeason = None
        trkType = None
        smk = simkl0rels
        simDat = simkl0rels
        aa = invAa

        # Properly config the ID
        if (platform == 'shikimori') and (re.match(r'^[a-zA-Z]+', id)):
            id = re.sub(r'^[a-zA-Z]+', '', id)
            await ctx.edit(f'Removed the prefix from the ID on `{platform}`', embeds=None)
            aa = await getNatsuAniApi(id=id, platform='shikimori')
        elif platform == 'simkl':
            simDat = await getSimklID(id, 'anime')
            simId = id
            malId = simDat['mal']
        elif platform in ['tmdb', 'tvdb', 'imdb']:
            try:
                if platform == 'tmdb':
                    id = id.split('/')
                    if len(id) > 1:
                        await ctx.edit(f'Season split is currently not supported on `{platform}`', embeds=None)
                        id = id[0]
                simId = await searchSimklId(id, platform=platform)
                simDat = await getSimklID(simId, 'anime')
                malId = simDat['mal']
            except KeyError:
                raise Exception(
                    f'No anime found on SIMKL with ID: `{id}` on `{platform}`')
        elif platform == 'trakt':
            try:
                if re.match(r'^(show|movie)s?\/[a-z0-9-]+(/season(s)?/[\d]+)$', id):
                    trkQuery = id.split('/')
                    trkType = trkQuery[0]
                    traktId = trkQuery[1]
                    if len(trkQuery) > 2:
                        trkSeason = trkQuery[3]
                    if trkType == "show":
                        trkType += "s"
                    elif trkType == "movie":
                        trkType += "s"
                else:
                    raise Exception(
                        'Invalid Trakt ID required by bot. Valid ID format: `shows/<slug-or-id>` and `movies/<slug-or-id>`.')
                trkData = await getTraktID(traktId, trkType)
                traktId = trkData['ids']['trakt']
                imdbId = trkData['ids']['imdb']
                tmdbId = trkData['ids']['tmdb']
                if trkSeason is not None:
                    aa = await getNatsuAniApi(id=f"{trkType}/{traktId}/seasons/{trkSeason}", platform='trakt')
                else:
                    aa = await getNatsuAniApi(id=f"{trkType}/{traktId}", platform='trakt')
                if aa['title'] is not None:
                    simId = await searchSimklId(title_id=aa['myanimelist'], platform='mal')
                elif (aa['title'] is None) and (imdbId is not None):
                    simId = await searchSimklId(title_id=imdbId, platform='imdb')
                elif (aa['title'] is None) and (tmdbId is not None):
                    mdtype = "show" if re.match(
                        r'shows?', trkType) else "movie"
                    simId = await searchSimklId(title_id=tmdbId, platform='tmdb', media_type=mdtype)

                simDat = await getSimklID(simkl_id=simId, media_type='anime')
                malId = simDat['mal']
            except aiohttp.ContentTypeError:
                raise Exception(
                    f'Title not found on the database, or you have entered the wrong ID/slug!')
            except KeyError:
                raise Exception(
                    f'Error while searching for the ID of `{platform}` via `imdb` and `tmdb` on SIMKL, entry may not linked with SIMKL counterpart, so unfortunately we can\'t reverse search for the relation')
        elif platform == 'kitsu':
            if re.match(r'^[a-zA-Z\-]+', id):
                # replace slug to id
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://kitsu.io/api/edge/anime?filter[slug]={id}') as resp:
                        if resp.status == 200:
                            kitsuData = await resp.json()
                            ktSlug = id
                            id = kitsuData['data'][0]['id']
                        else:
                            raise Exception(
                                f'Error while searching for the ID of `{platform}`')
                    await session.close()
                await ctx.edit(f'Replaced the slug (`{ktSlug}`) with the ID (`{id}`) on `{platform}`', embeds=None)
            aa = await getNatsuAniApi(id=id, platform=platform)
        elif platform == 'kaize':
            try:
                try:
                    aa = await getNatsuAniApi(id=id, platform=platform)
                except:
                    # check on slug using regex, if contains `-N` suffix, try to decrease by one,
                    # if `-N` is `-1`, remove completely the slug
                    # get the last number
                    lastNum = re.search(r'\d+$', uid).group()
                    # get the slug
                    slug = re.sub(r'-\d+$', '', uid)
                    # decrease the number by one
                    lastNum = int(lastNum) - 1
                    # if the number is 0, remove the suffix
                    if lastNum == 0:
                        uid = slug
                    else:
                        uid = f"{slug}-{lastNum}"
                    await ctx.edit(f"Searching for relations on `{platform}` using ID: `{uid}` (decrease by one)", embeds=None)
                    aa = await getNatsuAniApi(id=uid, platform=platform)
            except json.JSONDecodeError:
                raise Exception("""We've tried to search for the anime using the slug (and even fix the slug itself), but it seems that the anime is not found on Kaize via AnimeApi.
Please send a message to AnimeApi maintainer, nattadasu (he is also a developer of this bot)""")
        else:
            aa = await getNatsuAniApi(id=id, platform=platform)

        if (aa['title'] is None) and (malId is not None):
            aa = await getNatsuAniApi(id=malId, platform='myanimelist')

        # link SIMKL ID
        if platform not in ['simkl', 'trakt', 'tmdb', 'tvdb', 'imdb']:
            try:
                if aa['myanimelist'] is not None:
                    simId = await searchSimklId(title_id=aa['myanimelist'], platform='mal')
                    smk = await getSimklID(simkl_id=simId, media_type='anime')
                elif aa['anidb'] is not None:
                    simId = await searchSimklId(title_id=aa['anidb'], platform='anidb')
                    smk = await getSimklID(simkl_id=simId, media_type='anime')
            except:
                pass
        else:
            smk = simDat

        if (tmdbId is None) and (platform != 'tmdb'):
            tmdbId = smk['tmdb']
        elif platform == 'tmdb':
            tmdbId = id
        if (imdbId is None) and (platform != 'imdb'):
            imdbId = smk['imdb']
        elif platform == 'imdb':
            imdbId = id

        if (aa['title'] is None) and (simId != 0):
            title = smk['title']
        else:
            title = aa['title']

        if (aa['trakt'] is not None) and (platform != 'trakt'):
            trkType = aa['trakt_type']
            trkSeason = aa['trakt_season']
            traktId = f"{aa['trakt']}/seasons/{trkSeason}"
        elif (aa['trakt'] is None) and ((tmdbId is not None) or (imdbId is not None)) and (platform != 'trakt'):
            try:
                tid = imdbId
                lookup = f"imdb/{tid}"
                scpf = "IMDb"
                trkData = await lookupTrakt(lookup_param=lookup)
                trkType = trkData['type']
                traktId = trkData[trkType]['ids']['trakt']
            except KeyError:
                try:
                    tid = tmdbId
                    ttype = "movie" if smk['aniType'] == "movie" else "show" if (
                        (smk['aniType'] == "tv") or (smk['aniType'] == "ona")) else "movie"
                    lookup = f"tmdb/{tid}?type={ttype}"
                    scpf = "TMDB"
                    trkData = await lookupTrakt(lookup_param=lookup)
                    trkType = trkData['type']
                    traktId = trkData[trkType]['ids']['trakt']
                except KeyError:
                    pass

        relsEm = []
        # Get the relations
        if smk['allcin'] is not None:
            relsEm += [interactions.EmbedField(
                name="<:allcinema:1079493870326403123> AllCinema",
                value=f"[`{smk['allcin']}`](<https://www.allcinema.net/prog/show_c.php?num_c={smk['allcin']}>)",
                inline=True
            )]
        if (aa['anidb'] is not None) and (platform != 'anidb'):
            relsEm += [interactions.EmbedField(
                name="<:aniDb:1073439145067806801> AniDB",
                value=f"[`{aa['anidb']}`](<https://anidb.net/anime/{aa['anidb']}>)",
                inline=True
            )]
        if (aa['anilist'] is not None) and (platform != 'anilist'):
            relsEm += [interactions.EmbedField(
                name="<:aniList:1073445700689465374> AniList",
                value=f"[`{aa['anilist']}`](<https://anilist.co/anime/{aa['anilist']}>)",
                inline=True
            )]
        if smk['ann'] is not None:
            relsEm += [interactions.EmbedField(
                name="<:ann:1079377192951230534> Anime News Network",
                value=f"[`{smk['ann']}`](<https://www.animenewsnetwork.com/encyclopedia/anime.php?id={smk['ann']}>)",
                inline=True
            )]
        if (aa['animeplanet'] is not None) and (platform != 'animeplanet'):
            relsEm += [interactions.EmbedField(
                name="<:animePlanet:1073446927447891998> Anime-Planet",
                value=f"[`{aa['animeplanet']}`](<https://www.anime-planet.com/anime/{aa['animeplanet']}>)",
                inline=True
            )]
        if (aa['anisearch'] is not None) and (platform != 'anisearch'):
            relsEm += [interactions.EmbedField(
                name="<:aniSearch:1073439148100300810> aniSearch",
                value=f"[`{aa['anisearch']}`](<https://anisearch.com/anime/{aa['anisearch']}>)",
                inline=True
            )]
        if (aa['annict'] is not None) and (platform != 'annict'):
            relsEm += [interactions.EmbedField(
                name="<:annict:1088801941469012050> Annict",
                value=f"[`{aa['annict']}`](<https://annict.com/works/{aa['annict']}>) ([En](<https://en.annict.com/works/{aa['annict']}>))",
                inline=True
            )]
        if (imdbId is not None) and (platform != "imdb"):
            relsEm += [interactions.EmbedField(
                name="<:IMDb:1079376998880784464> IMDb",
                value=f"[`{imdbId}`](<https://www.imdb.com/title/{imdbId}>)",
                inline=True
            )]
        if (aa['kaize'] is not None) and (platform != 'kaize'):
            relsEm += [interactions.EmbedField(
                name="<:kaize:1073441859910774784> Kaize",
                value=f"[`{aa['kaize']}`](<https://kaize.io/anime/{aa['kaize']}>)",
                inline=True
            )]
        if (aa['kitsu'] is not None) and (platform != 'kitsu'):
            relsEm += [interactions.EmbedField(
                name="<:kitsu:1073439152462368950> Kitsu",
                value=f"[`{aa['kitsu']}`](<https://kitsu.io/anime/{aa['kitsu']}>)",
                inline=True
            )]
        if (aa['livechart'] is not None) and (platform != 'livechart'):
            relsEm += [interactions.EmbedField(
                name="<:liveChart:1073439158883844106> LiveChart",
                value=f"[`{aa['livechart']}`](<https://livechart.me/anime/{aa['livechart']}>)",
                inline=True
            )]
        if (aa['myanimelist'] is not None) and (platform != 'myanimelist'):
            relsEm += [interactions.EmbedField(
                name="<:myAnimeList:1073442204921643048> MyAnimeList",
                value=f"[`{aa['myanimelist']}`](<https://myanimelist.net/anime/{aa['myanimelist']}>)",
                inline=True
            )]
        if (aa['notify'] is not None) and (platform != 'notify'):
            relsEm += [interactions.EmbedField(
                name="<:notifyMoe:1073439161194905690> Notify",
                value=f"[`{aa['notify']}`](<https://notify.moe/anime/{aa['notify']}>)",
                inline=True
            )]
        if (aa['shikimori'] is not None) and (platform != 'shikimori'):
            relsEm += [interactions.EmbedField(
                name="<:shikimori:1073441855645155468> Shikimori",
                value=f"[`{aa['shikimori']}`](<https://shikimori.one/animes/{aa['shikimori']}>)",
                inline=True
            )]
        if (aa['shoboi'] is not None) and (platform != 'shoboi'):
            relsEm += [interactions.EmbedField(
                name="<:shoboi:1088801950751015005> Shoboi Calendar",
                value=f"[`{aa['shoboi']}`](<https://cal.syoboi.jp/tid/{aa['shoboi']}>)",
                inline=True
            )]
        if (aa['otakotaku'] is not None) and (platform != 'otakotaku'):
            relsEm += [interactions.EmbedField(
                name="<:otakOtaku:1088801946313429013> Otak Otaku",
                value=f"[`{aa['otakotaku']}`](<https://otakotaku.com/anime/view/{aa['otakotaku']}>)",
                inline=True
            )]
        if (aa['silveryasha'] is not None) and (platform != 'silveryasha'):
            relsEm += [interactions.EmbedField(
                name="<:silverYasha:1079380182059733052> Silver Yasha",
                value=f"[`{aa['silveryasha']}`](<https://db.silveryasha.web.id/anime/{aa['silveryasha']}>)",
                inline=True
            )]
        if (simId != 0) and (platform != 'simkl'):
            relsEm += [interactions.EmbedField(
                name="<:simkl:1073630754275348631> SIMKL",
                value=f"[`{simId}`](<https://simkl.com/{smk['type']}/{simId}>)",
                inline=True
            )]
        if (traktId is not None) and (platform != "trakt"):
            relsEm += [interactions.EmbedField(
                name=f"<:trakt:1081612822175305788> Trakt",
                value=f"[`{traktId}`](<https://trakt.tv/{trkType}/{traktId}>)",
                inline=True
            )]
        try:
            if traktId is not None:
                if re.search(r"^shows?$", trkType):
                    tvtyp = "series"
                    tmtyp = "tv"
                else:
                    tvtyp = "movies"
                    tmtyp = "movie"
            else:
                if smk['aniType'] == "tv":
                    tvtyp = "series"
                    tmtyp = "tv"
                elif smk['aniType'] is not None:
                    tvtyp = "movies"
                    tmtyp = "movie"
        except:
            tvtyp = "series"
            tmtyp = "tv"
        if (tmdbId is not None) and (platform != "tmdb"):
            if trkSeason is not None:
                tmdbId = f"{tmdbId}/season/{trkSeason}"
            relsEm += [interactions.EmbedField(
                name="<:tmdb:1079379319920529418> The Movie Database",
                value=f"[`{tmdbId}`](<https://www.themoviedb.org/{tmtyp}/{tmdbId}>)",
                inline=True
            )]
        if (smk['tvdb'] is not None) and (platform != "tvdb"):
            relsEm += [interactions.EmbedField(
                name="<:tvdb:1079378495064510504> The TVDB",
                value=f"[`{smk['tvdb']}`](<https://www.thetvdb.com/?tab={tvtyp}&id={smk['tvdb']}>)",
                inline=True
            )]
        elif (smk['tvdbslug'] is not None) and (platform != "tvdb"):
            if trkSeason is not None:
                tvdbId = f"{smk['tvdbslug']}/seasons/official/{trkSeason}"
            else:
                tvdbId = smk['tvdbslug']
            relsEm += [interactions.EmbedField(
                name="<:tvdb:1079378495064510504> The TVDB",
                value=f"[`{tvdbId}`](<https://www.thetvdb.com/{tvtyp}/{tvdbId}>)",
                inline=True
            )]

        if (platform == 'tvdb') and (re.match(r"^[\d]+$", id)):
            tvdbId = f"https://www.thetvdb.com/?tab={tvtyp}&id={id}"
        elif (platform == 'tvdb'):
            tvdbId = f"https://www.thetvdb.com/{tvtyp}/{id}"
        else:
            tvdbId = None

        col = getPlatformColor(platform)

        if platform == 'trakt':
            media_id = f"{trkType}/{traktId}"
        elif platform == 'tvdb':
            media_id = tvdbId
        elif platform == 'tmdb':
            media_id = f"{tmtyp}/{id}"
        else:
            media_id = id

        pfs = mediaIdToPlatform(media_id=media_id, platform=platform)
        pf = pfs['pf']
        uid = pfs['uid']
        emoid = pfs['emoid']

        if smk['poster'] is not None:
            poster = f"https://simkl.in/posters/{smk['poster']}_m.webp"
            postsrc = "SIMKL"
        elif aa['kitsu'] is not None:
            poster = f"https://media.kitsu.io/anime/poster_images/{aa['kitsu']}/large.jpg"
            postsrc = "Kitsu"
        elif aa['notify'] is not None:
            poster = f"https://media.notify.moe/images/anime/original/{aa['notify']}.jpg"
            postsrc = "Notify.moe"
        else:
            poster = None
            postsrc = None

        if postsrc is not None:
            postsrc = f" Poster from {postsrc}"
        else:
            postsrc = ""

        uAu = uid.split('/')
        uAu = uAu[0] + "//" + uAu[2]

        if title is not None:
            dcEm = interactions.Embed(
                author=interactions.EmbedAuthor(
                    name=f"Looking external site relations from {pf}",
                    icon_url=f"https://cdn.discordapp.com/emojis/{emoid}.png?v=1",
                    url=uAu
                ),
                title=f"{title}",
                url=uid,
                description="Data might be inaccurate, especially for sequels of the title (as IMDb, TVDB, TMDB, and Trakt relies on per title entry than season entry)",
                color=col,
                fields=relsEm,
                footer=interactions.EmbedFooter(
                    text=f"Powered by nattadasu's AnimeAPI, Trakt, and SIMKL.{postsrc}"
                ),
                thumbnail=interactions.EmbedImageStruct(
                    url=poster
                )
            )
        else:
            raise Exception(
                f"No relations found on {pf} with following url: <{uid}>!\nEither the anime is not in the database, or you have entered the wrong ID.")
        await ctx.edit("", embeds=dcEm)

    except Exception as e:
        if e == 'Expecting value: line 1 column 1 (char 0)':
            e = 'No relations found!\nEither the anime is not in the database, or you have entered the wrong ID.'
        else:
            e = e
        e = f"""While getting the relations for `{platform}` with id `{id}`, we got error message: {e}"""
        dcEm = exceptionsToEmbed(returnException(e))

        await ctx.edit("", embeds=dcEm)


@bot.command(
    name="random_nekomimi",
    description="Get a random image of characters with cat ears, powered by Natsu's nekomimiDb!"
)
async def random_nekomimi(ctx: interactions.CommandContext):
    pass


@random_nekomimi.subcommand()
async def bois(ctx: interactions.CommandContext):
    """Get a random image of male character with cat ears!"""
    await ctx.defer()
    row = await getNekomimi('boy')
    # get the image url
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=col,
        author=interactions.EmbedAuthor(
            name="Powered by Natsu's nekomimiDb",
            url="https://github.com/nattadasu/nekomimiDb"
        ),
        fields=[
            interactions.EmbedField(
                name="Image source",
                value=f"[Click here]({imageSourceUrl})",
                inline=True
            ),
            interactions.EmbedField(
                name="Artist",
                value=f"[{artist}]({artistUrl})",
                inline=True
            )
        ]
    )
    await ctx.send("", embeds=dcEm)


@random_nekomimi.subcommand()
async def gurls(ctx: interactions.CommandContext):
    """Get a random image of female character with cat ears!"""
    await ctx.defer()
    row = await getNekomimi('girl')
    # get the image url
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=col,
        author=interactions.EmbedAuthor(
            name="Powered by Natsu's nekomimiDb",
            url="https://github.com/nattadasu/nekomimiDb"
        ),
        fields=[
            interactions.EmbedField(
                name="Image source",
                value=f"[Click here]({imageSourceUrl})",
                inline=True
            ),
            interactions.EmbedField(
                name="Artist",
                value=f"[{artist}]({artistUrl})",
                inline=True
            )
        ]
    )
    await ctx.send("", embeds=dcEm)


@random_nekomimi.subcommand()
async def true_random(ctx: interactions.CommandContext):
    """Get a random image of characters with cat ears, whatever the gender they are!"""
    await ctx.defer()
    row = await getNekomimi()
    # get the image url
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=col,
        author=interactions.EmbedAuthor(
            name="Powered by Natsu's nekomimiDb",
            url="https://github.com/nattadasu/nekomimiDb"
        ),
        fields=[
            interactions.EmbedField(
                name="Image source",
                value=f"[Click here]({imageSourceUrl})",
                inline=True
            ),
            interactions.EmbedField(
                name="Artist",
                value=f"[{artist}]({artistUrl})",
                inline=True
            )
        ]
    )
    await ctx.send("", embeds=dcEm)


@bot.command(
    name="manga",
    description="Get information about a manga, powered by AniList!"
)
async def manga(ctx: interactions.CommandContext):
    pass


@manga.subcommand(
    name="search",
    description="Search for a manga!",
    options=[
        interactions.Option(
            name="title",
            description="The title of the manga you want to search for",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def search(ctx: interactions.CommandContext, title: str):
    """Search for a manga!"""
    await ctx.defer()
    await ctx.get_channel()
    trailer = None
    # get the manga
    try:
        rawData = await searchAniList(name=title, media_id=None, isAnime=False)
        bypass = await bypassAniListEcchiTag(alm=rawData[0])
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        dcEm = await generateAnilist(alm=rawData[0], isNsfw=nsfw_bool, bypassEcchi=bypass)
        if (rawData[0]['trailer'] is not None) and (rawData[0]['trailer']['site'] == "youtube"):
            trailer = generateTrailer(data=rawData[0]['trailer'])
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        trailer = None

    await ctx.send("", embeds=dcEm, components=trailer)


@manga.subcommand(
    options=[
        interactions.Option(
            name="id",
            description="The manga ID on AniList to fetch",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def info(ctx: interactions.CommandContext, id: int):
    """Get manga information from AniList using AniList ID"""
    await ctx.defer()
    await ctx.get_channel()
    trailer = None
    # get the manga
    try:
        rawData = await searchAniList(name=None, media_id=id, isAnime=False)
        bypass = await bypassAniListEcchiTag(alm=rawData[0])
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        dcEm = await generateAnilist(alm=rawData[0], isNsfw=nsfw_bool, bypassEcchi=bypass)
        if (rawData[0]['trailer'] is not None) and (rawData[0]['trailer']['site'] == "youtube"):
            trailer = generateTrailer(data=rawData[0]['trailer'])
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        trailer = None

    await ctx.send("", embeds=dcEm, components=trailer)


@bot.command(
    name="invite",
    description="Invite me to your server!"
)
async def invite(ctx: interactions.CommandContext):
    invLink = f"https://discord.com/api/oauth2/authorize?client_id={BOT_CLIENT_ID}&permissions=274878221376&scope=bot%20applications.commands"
    dcEm = interactions.Embed(
        title=f"{EMOJI_ATTENTIVE} Thanks for your interest in inviting me to your server!",
        color=0x996422,
        description="To invite me, simply press \"**Invite me!**\" button below!\nFor any questions, please join my support server!",
        fields=[
            interactions.EmbedField(
                name="Required permissions/access",
                value="Read Messages, Send Messages, Send Messages in Thread, Embed Links, Attach Files, Use External Emojis, Add Reactions",
                inline=True
            ),
            interactions.EmbedField(
                name="Required scopes",
                value="`bot`\n`applications.commands`",
                inline=True
            )
        ]
    )
    invBotton = interactions.Button(
        type=interactions.ComponentType.BUTTON,
        style=interactions.ButtonStyle.LINK,
        label="Invite me!",
        url=invLink
    )
    servBotton = interactions.Button(
        type=interactions.ComponentType.BUTTON,
        style=interactions.ButtonStyle.LINK,
        label="Support server",
        url=BOT_SUPPORT_SERVER
    )
    await ctx.send(embeds=dcEm, components=[invBotton, servBotton])


@bot.command(
    name="support",
    description="Give support to the bot!"
)
async def support(ctx: interactions.CommandContext):
    sendMessages = f"""{EMOJI_ATTENTIVE} Thanks for your interest in supporting me!

You can support me on [Ko-Fi](<https://ko-fi.com/nattadasu>), [PayPal](<https://paypal.me/nattadasu>), or [GitHub Sponsors](<https://github.com/sponsors/nattadasu>).

For Indonesian users, you can use [Trakteer](<https://trakteer.id/nattadasu>) or [Saweria](<https://saweria.co/nattadasu>).

Or, are you a developer? You can contribute to the bot's code on [GitHub](<https://github.com/nattadasu/ryuuRyuusei>)

If you have any questions (or more payment channels), please join my [support server]({BOT_SUPPORT_SERVER})!"""

    await ctx.send(sendMessages)


@bot.command(
    name="lastfm",
    description="Show Last.FM information about user!",
    options=[
        interactions.Option(
            name="username",
            description="User to lookup",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="maximum",
            description="Maximum scrobbled tracks to show",
            type=interactions.OptionType.INTEGER,
            min_value=0,
            max_value=15,
            required=False
        )
    ]
)
async def lastfm(ctx: interactions.CommandContext, username: str, maximum: int = 9):
    await ctx.defer()
    await ctx.send(f"Fetching data for {username}...", embeds=None)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={username}&api_key={LASTFM_API_KEY}&format=json') as resp:
                if resp.status == 404:
                    raise Exception(
                        "User can not be found on Last.fm. Check the name or register?")
                else:
                    jsonText = await resp.text()
                    jsonFinal = jload(jsonText)
                    ud = jsonFinal['user']
            await session.close()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={LASTFM_API_KEY}&format=json&limit=9') as resp:
                jsonText = await resp.text()
                jsonFinal = jload(jsonText)
                scb = jsonFinal['recenttracks']['track']
            await session.close()
        tracks = []
        # trim scb if items more than {maximum}
        if maximum > 0:
            if maximum > 1:
                rpt = "\n\n**Recently played tracks**"
            else:
                rpt = "\n\n**Recently played track**"
            if len(scb) > maximum:
                scb = scb[:maximum]
            nRep = 1
            for tr in scb:
                try:
                    if tr['@attr']['nowplaying'] is not None:
                        np = jload(tr['@attr']['nowplaying'].lower())
                except:
                    np = False
                # sanitize title to be markdown compatible
                tr['name'] = sanitizeMarkdown(str(tr['name']))
                tr['artist']['#text'] = sanitizeMarkdown(
                    str(tr['artist']['#text']))
                tr['album']['#text'] = sanitizeMarkdown(
                    str(tr['album']['#text']))
                scu = tr['url']
                scus = scu.split("/")
                # assumes the url as such: https://www.last.fm/music/Artist/_/Track
                # so, the artist is at index 4, and track is at index 6
                # in index 4 and 6, encode the string to be url compatible with percent encoding
                track = []
                for art in scus[6].split("+"):
                    track.append(urlquote(art))
                track = "+".join(track)
                track = track.replace('%25', '%')

                artist = []
                for art in scus[4].split("+"):
                    artist.append(urlquote(art))
                artist = "+".join(artist)
                artist = artist.replace('%25', '%')

                tr['url'] = f"https://www.last.fm/music/{artist}/_/{track}"

                if np is True:
                    title = f"▶️ {tr['name']}"
                    dt = "*Currently playing*"
                else:
                    title = tr['name']
                    dt = int(tr['date']['uts'])
                    dt = f"<t:{dt}:R>"
                tracks += [interactions.EmbedField(
                    name=title,
                    value=f"""{tr['artist']['#text']}
{tr['album']['#text']}
{dt}, [Link]({tr['url']})""",
                    inline=True
                )]
                nRep += 1
        else:
            rpt = ""
        # read ud['images'], and grab latest one
        imgLen = len(ud['image'])
        img = ud['image'][imgLen - 1]['#text']
        lfmpro = ud['subscriber']
        icShine = "<:icons_shine1:859424400959602718>"
        if lfmpro == "1":
            lfmpro = f"{icShine} Last.FM Pro User\n"
            badge = icShine + " "
        else:
            lfmpro, badge = "", ""
        # building embed
        dcEm = interactions.Embed(
            author=interactions.EmbedAuthor(
                name="Last.FM Profile",
                url="https://last.fm",
                icon_url="https://media.discordapp.net/attachments/923830321433149453/1079483003396432012/Tx1ceVTBn2Xwo2dF.png"
            ),
            title=f"{badge}{ud['name']}'s Last.FM Profile",
            url=ud['url'],
            color=0xF71414,
            description=f"""{lfmpro}Real name: {ud['realname']}
Account created: <t:{ud['registered']['#text']}:D> (<t:{ud['registered']['#text']}:R>)
Total scrobbles: {ud['playcount']}
🧑‍🎤 {ud['artist_count']}  💿 {ud['album_count']} 🎶 {ud['track_count']}{rpt}""",
            thumbnail=interactions.EmbedImageStruct(
                url=img
            ),
            fields=tracks
        )
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))

    await ctx.edit("", embeds=dcEm)


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
    await ctx.defer(ephemeral=True)
    discordId = dc_username.id
    discordUsername = dc_username.username
    discordDiscriminator = dc_username.discriminator
    discordJoined = int(snowflake_to_datetime(dc_username.id))
    discordServerName = ctx.guild.name
    malUname = mal_username.strip()
    try:
        if checkIfRegistered(discordId):
            sendMessages = f"""{EMOJI_DOUBTING} **User is already registered!**"""
        else:
            jikanData = await getJikanData(malUname)
            malUid = jikanData['mal_id']
            jikanData['joined'] = jikanData['joined'].replace(
                '+00:00', '+0000')
            malJoined = int(datetime.datetime.strptime(
                jikanData['joined'], "%Y-%m-%dT%H:%M:%S%z").timestamp())
            registeredAt = int(datetime.datetime.now().timestamp())
            registeredGuild = ctx.guild_id
            registeredBy = ctx.author.id
            sendMessages = f"""{EMOJI_SUCCESS} **User registered!**```json
{{
    "discordId": {discordId},
    "discordUsername": "{discordUsername}#{discordDiscriminator}",
    "discordJoined": {discordJoined},
    "registeredGuildId": {registeredGuild},
    "registeredGuildName": "{discordServerName}",
    "malUname": "{malUname}",
    "malId": {malUid},
    "malJoined": {malJoined},
    "registeredAt": {registeredAt},
    "registeredBy": {registeredBy} // it's you, {ctx.author.username}#{ctx.author.discriminator}!
}}```"""
            saveToDatabase(discordId, f'{discordUsername}#{discordDiscriminator}', discordJoined, str(
                malUname), malUid, malJoined, registeredAt, registeredGuild, registeredBy, discordServerName)
    except Exception as e:
        sendMessages = returnException(e)

    await ctx.send(sendMessages, ephemeral=True)


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
    await ctx.defer(ephemeral=True)
    discordId = dc_username.id
    if checkIfRegistered(discordId):
        try:
            dropUser(discordId=discordId)
            sendMessages = f"""{EMOJI_SUCCESS} **User unregistered!**"""
        except Exception as e:
            sendMessages = returnException(e)
    else:
        sendMessages = f"""{EMOJI_DOUBTING} **User is not registered!**"""

    await ctx.send(sendMessages, ephemeral=True)


@bot.command(
    name="admin_verify",
    description="Verify user for the server, for admin only!",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=[
        int(VERIFICATION_SERVER)
    ],
    options=[
        interactions.Option(
            name="username",
            description="User to verify",
            type=interactions.OptionType.USER,
            required=True
        )
    ]
)
async def admin_verify(ctx: interactions.CommandContext, username: int):
    await ctx.defer()
    discordId = username.id
    # get user joined date
    discordJoined = snowflake_to_datetime(discordId)
    discordJoined = int(discordJoined)
    getMemberDetail = await ctx.guild.get_member(discordId)
    memberRoles = getMemberDetail.roles
    verifiedRole = VERIFIED_ROLE

    try:
        if discordId == ctx.author.id:
            raise Exception(
                f"{EMOJI_USER_ERROR} Sorry, but you can't verify yourself!")
        elif int(verifiedRole) in memberRoles:
            raise Exception(f"{EMOJI_USER_ERROR} User have already verified.")

        verified = await verifyUser(discordId=discordId)
        if verified is True:
            botHttp = interactions.HTTPClient(token=BOT_TOKEN)
            await botHttp.add_member_role(guild_id=ctx.guild_id, user_id=discordId, role_id=verifiedRole, reason=f"Verified by {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")
            sendMessages = f"{EMOJI_SUCCESS} User <@!{discordId}> has been verified"
        elif verified is False:
            raise Exception(f"{EMOJI_DOUBTING} User may have not joined the club yet, or the bot currently only check a page. Please raise an issue to this bot maintainer")
    except Exception as e:
        sendMessages = returnException(e)

    await ctx.send(sendMessages)

@bot.command(
    name="games",
    description="Get information about games! Powered by RAWG"
)
async def games(ctx: interactions.CommandContext):
    pass

@games.subcommand(
    options=[
        interactions.Option(
            name="title",
            description="The title of the game",
            required=True,
            type=interactions.OptionType.STRING,
        )
    ]
)
async def search(ctx: interactions.CommandContext, title: str):
    """Search for a title in RAWG"""
    await ctx.defer()
    try:
        results = await searchRawg(query=title)
        f = []
        so = []
        for r in results:
            rhel = r['released']
            f += [
                interactions.EmbedField(
                    name=r['name'],
                    value=f"*Released on: {rhel}*",
                    inline=False
                )
            ]
            so += [
                interactions.SelectOption(
                    label=r['name'],
                    value=r['slug'],
                    description=f"Released: {rhel}"
                )
            ]
        dcEm = interactions.Embed(
            author=interactions.EmbedAuthor(
                name="RAWG Game",
                url=f"https://rawg.io/",
                icon_url="https://pbs.twimg.com/profile_images/951372339199045632/-JTt60iX_400x400.jpg"
            ),
            thumbnail=interactions.EmbedImageStruct(
                url="https://pbs.twimg.com/profile_images/951372339199045632/-JTt60iX_400x400.jpg"
            ),
            color=0x1F1F1F,
            title="Search Results",
            description=f"Found **{len(results)} results** for `{title}`, please select by choosing right option in the dropdown below",
            fields=f
        )
        com = [
            interactions.SelectMenu(
                options=so,
                custom_id="rawg_search",
                placeholder="Select a game to get more information"
            )
        ]

        await ctx.send("", embeds=dcEm, components=com)
        # timeout the selection
        await asyncio.sleep(90)
        await ctx.edit("*Selection had reached timeout*", embeds=dcEm, components=[])
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        await ctx.send("", embeds=dcEm)


@bot.component("rawg_search")
async def rawg_search(ctx: interactions.ComponentContext, choices: list[str]):
    await ctx.defer()
    try:
        gameData = await getRawgData(slug=choices[0])
        dcEm = await generateRawg(data=gameData)
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))

    await ctx.edit(embeds=dcEm, components=[])

@games.subcommand(
    options=[
        interactions.Option(
            name="slug",
            description="The game slug/id on RAWG to fetch",
            required=True,
            type=interactions.OptionType.STRING,
        )
    ]
)
async def info(ctx: interactions.CommandContext, slug: str):
    """Get game information from RAWG using RAWG slug/ID"""
    await ctx.defer()
    try:
        gameData = await getRawgData(slug=slug)
        dcEm = await generateRawg(data=gameData)
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))

    await ctx.send("", embeds=dcEm)


print("Starting bot...")

bot.start()
