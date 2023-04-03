#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cspell:disable

from modules.commons import *
from modules.const import *

from modules.anilist import *
from modules.animeapi import *
from modules.database import *
from modules.kitsu import *
from modules.lastfm import *
from modules.myanimelist import *
from modules.nekomimidb import *
from modules.platforms import *
from modules.rawg import *
from modules.relations import *
from modules.simkl import *
from modules.trakt import *


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
        messages = DECLINED_GDPR
        await ctx.send(messages, ephemeral=True)
        return
    else:
        discordId = str(ctx.user.id)
        discordUsername = str(ctx.user.username)
        discordDiscrim = str(ctx.user.discriminator)
        discordServer = ctx.guild
        whois = f"{discordUsername}#{discordDiscrim}"

        try:
            messages = await registerUser(whois=whois, discordId=discordId, server=discordServer, malUsername=mal_username)
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
        dcEm = exceptionsToEmbed(returnException(
            "User can not be found if they're joined this server or not."))
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

    userRegistered = MESSAGE_MEMBER_REG_PROFILE

    if (user is not None) and (mal_username is not None):
        try:
            raise KeyError
        except KeyError:
            sendMessages = ""
            dcEm = exceptionsToEmbed(returnException(
                f"{EMOJI_USER_ERROR} **You cannot use both options!** Use either one of `user:` or `mal_username:`, hmph. >:("))
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

                    dcEm = generateProfile(
                        malProfile=malProfile, extend=extended)
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

                dcEm = generateProfile(malProfile=malProfile, extend=extended)
            except Exception as e:
                sendMessages = ""
                dcEm = exceptionsToEmbed(definejikanException(e))

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
    messages = ABOUT_BOT
    await ctx.send(messages)


@bot.command(
    name="privacy",
    description="Read privacy policy of this bot, especially for EU (GDPR) and California (CPRA/CCPA) users!"
)
async def privacy(ctx: interactions.CommandContext):
    messages = PRIVACY_POLICY

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
        userRow = exportUserData(userId=userId)
        dcEm = interactions.Embed(
            title="Data Exported!",
            description=f"""{EMOJI_SUCCESS} **Here's your data!**
```json
{userRow}
```
Quick PSA: the exported data in this JSON is exactly the same as the data stored in the bot's database.""",
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
        if len(alData) == 0:
            raise Exception()
        else:
            for a in alData:
                a["format"] = str(a["format"]).capitalize()
                a["status"] = str(a["status"]).replace('_', ' ').capitalize()
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
            searchFrom = "AniList"
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
                searchFrom = "Jikan"
        except:
            aniFound = False

    if aniFound is True:
        try:
            dcEm = generateSearchSelections(
                color=0x2F51A3,
                homepage="https://myanimelist.net",
                icon="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png",
                platform="MyAnimeList Anime",
                query=title,
                results=f,
                title=f"Search Results via {searchFrom}",
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
        await ctx.edit(MESSAGE_SELECT_TIMEOUT, embeds=dcEm, components=[])


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
                trailer = generateTrailer(
                    data=alData[0]['trailer'], isMal=False)
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

    ani_id = lookupRandomAnime()
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
            aaDict = await getAniList(media_id=aniApi['anilist'], isAnime=True)
            if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                trailer = generateTrailer(data=aaDict[0]['trailer'])
        else:
            try:
                aaDict = await getAniList(name=aniApi['title'], media_id=None, isAnime=True)
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
            aaDict = await getAniList(media_id=aniApi['anilist'], isAnime=True)
            if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                trailer = generateTrailer(data=aaDict[0]['trailer'])
        else:
            try:
                aaDict = await getAniList(name=aniApi['title'], media_id=None, isAnime=True)
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
        tvdbId = None
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
                raise Exception(ERR_KAIZE_SLUG_MODDED)
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
        isSlug = False

        if trkSeason is not None:
            if smk['tvdb'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    f"?tab={tvtyp}&id={smk['tvdb']}"
            elif smk['tvdbslug'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    f"{tvtyp}/{smk['tvdbslug']}/seasons/official/{trkSeason}"
                isSlug = True
            tmdbId = f"{tmtyp}/{tmdbId}/season/{trkSeason}"
        else:
            if smk['tvdb'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    f"?tab={tvtyp}&id={smk['tvdb']}"
            elif smk['tvdbslug'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    tvtyp + '/' + smk['tvdbslug']
                isSlug = True
            tmdbId = tmtyp + '/' + str(tmdbId)

        relsEm = platformsToFields(
            currPlatform=platform,
            allcin=smk['allcin'],
            anidb=aa['anidb'],
            anilist=aa['anilist'],
            ann=smk['ann'],
            animeplanet=aa['animeplanet'],
            anisearch=aa['anisearch'],
            annict=aa['annict'],
            imdb=imdbId,
            kaize=aa['kaize'],
            kitsu=aa['kitsu'],
            livechart=aa['livechart'],
            myanimelist=aa['myanimelist'],
            notify=aa['notify'],
            otakotaku=aa['otakotaku'],
            shikimori=aa['shikimori'],
            shoboi=aa['shoboi'],
            silveryasha=aa['silveryasha'],
            simkl=simId,
            simklType=smk['type'],
            trakt=traktId,
            tvdb=tvdbId,
            tmdb=tmdbId,
            tvtyp=tvtyp,
            isSlug=isSlug,
        )

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
    data = await getNekomimi('boy')
    dcEm = generateNekomimi(row=data)
    await ctx.send("", embeds=dcEm)


@random_nekomimi.subcommand()
async def gurls(ctx: interactions.CommandContext):
    """Get a random image of female character with cat ears!"""
    await ctx.defer()
    data = await getNekomimi('girl')
    dcEm = generateNekomimi(row=data)
    await ctx.send("", embeds=dcEm)


@random_nekomimi.subcommand()
async def true_random(ctx: interactions.CommandContext):
    """Get a random image of characters with cat ears, whatever the gender they are!"""
    await ctx.defer()
    data = await getNekomimi()
    dcEm = generateNekomimi(row=data)
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
    """Search manga using the title."""
    await ctx.defer()
    try:
        results = await searchAniList(name=title, isAnime=False)
        f = []
        so = []
        if len(results) == 0:
            raise ValueError()
        for r in results:
            # only capitalize the first letter of the format and status
            r["format"] = str(r["format"]).capitalize()
            r["status"] = str(r["status"]).replace('_', ' ').capitalize()
            f += [
                interactions.EmbedField(
                    name=r["title"]["romaji"],
                    value=f"""*{r['title']['native']}, {r['format']}, {r['status']}*""",
                    inline=False
                )
            ]
            so += [
                interactions.SelectOption(
                    label=r["title"]["romaji"],
                    value=r["id"],
                    description=f"""{r['format']}, {r['status']}""",
                )
            ]
        dcEm = generateSearchSelections(
            color=0x2F80ED,
            homepage="https://anilist.co/",
            icon="https://anilist.co/img/icons/android-chrome-192x192.png",
            platform="AniList Manga",
            query=title,
            results=f,
            title="Search Results",
        )
        com = [
            interactions.SelectMenu(
                options=so,
                custom_id="anilist_search",
                placeholder="Select a manga to get more information"
            )
        ]
        await ctx.send("", embeds=dcEm, components=com)
        await asyncio.sleep(90)
        await ctx.edit(MESSAGE_SELECT_TIMEOUT, embeds=dcEm, components=[])
    except ValueError:
        dcEm = exceptionsToEmbed(error=f"""We couldn't able to find any manga with that title (`{title}`). Please check the spelling!
**Pro tip**: Use Native title to get most accurate result.... that if you know how to type in such language.""")
        await ctx.send("", embeds=dcEm, components=[])
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        await ctx.send("", embeds=dcEm, components=[])


@bot.component("anilist_search")
async def anilist_search(ctx: interactions.ComponentContext, choices: list[str]):
    await ctx.defer()
    await ctx.get_channel()
    trailer = None
    try:
        rawData = await getAniList(media_id=int(choices[0]), isAnime=False)
        bypass = await bypassAniListEcchiTag(alm=rawData[0])
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
        rawData = await getAniList(media_id=id, isAnime=False)
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
        description=MESSAGE_INVITE,
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
    sendMessages = SUPPORT_DEVELOPMENT

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
            max_value=21,
            required=False
        )
    ]
)
async def lastfm(ctx: interactions.CommandContext, username: str, maximum: int = 9):
    await ctx.defer()
    await ctx.send(f"Fetching data for {username}...", embeds=None)
    try:
        dcEm = await generateLastFm(username=username, maximum=maximum)
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
    discordServer = ctx.guild
    whois = f"{discordUsername}#{discordDiscriminator}"
    try:
        sendMessages = await registerUser(whois=whois, discordId=discordId, server=discordServer, malUsername=mal_username, actor=ctx.author)
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
            raise Exception(
                f"{EMOJI_DOUBTING} User may have not joined the club yet, or the bot currently only check a page. Please raise an issue to this bot maintainer")
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
        dcEm = generateSearchSelections(
            color=0x1F1F1F,
            homepage="https://rawg.io/",
            icon="https://pbs.twimg.com/profile_images/951372339199045632/-JTt60iX_400x400.jpg",
            platform="RAWG Games",
            query=title,
            results=f,
            title="Search Results",
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
        await ctx.edit(MESSAGE_SELECT_TIMEOUT, embeds=dcEm, components=[])
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
