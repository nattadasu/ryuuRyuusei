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
from modules.tmdb import *
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
    await malProfileSubmit(ctx=ctx, user=user, mal_username=mal_username, extended=extended)


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

    f = []
    so = []
    com = []
    aniFound = False

    try:
        await ctx.send(f"Searching `{title}` using AniList", embeds=None, components=None)
        alData = await searchAniList(name=title, isAnime=True)
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
            ani = await searchJikanAnime(title=title)
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
    ani_id: int = int(choices[0])
    await malSubmit(ctx, ani_id, 'anime')


@anime.subcommand()
async def random(ctx: interactions.CommandContext):
    """Get random anime information from MAL"""
    await ctx.defer()

    ani_id = lookupRandomAnime()

    await ctx.send(f"Found [`{ani_id}`](<https://myanimelist.net/anime/{ani_id}>), showing information...", ephemeral=True)

    await malSubmit(ctx, ani_id, 'anime')


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
    await malSubmit(ctx, id, 'anime')


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
    await relationsSubmit(ctx, id=id, platform=platform)


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
    await nekomimiSubmit(ctx, 'boy')


@random_nekomimi.subcommand()
async def gurls(ctx: interactions.CommandContext):
    """Get a random image of female character with cat ears!"""
    await ctx.defer()
    await nekomimiSubmit(ctx, 'girl')


@random_nekomimi.subcommand()
async def true_random(ctx: interactions.CommandContext):
    """Get a random image of characters with cat ears, whatever the gender they are!"""
    await ctx.defer()
    await nekomimiSubmit(ctx, None)


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
    id: int = int(choices[0])
    await anilistSubmit(ctx, id, mediaType='manga')


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
    await anilistSubmit(ctx, id, mediaType='manga')


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
    await rawgSubmit(ctx=ctx, slug=choices[0])


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
    await rawgSubmit(ctx=ctx, slug=slug)


@bot.command(
    name="tv",
    description="Get information about TV Shows! Powered by SIMKL and The Movie Database (for NSFW checker)"
)
async def tv(ctx: interactions.CommandContext):
    pass


@bot.command(
    name="movie",
    description="Get information about Movies! Powered by SIMKL and The Movie Database (for NSFW checker)"
)
async def movie(ctx: interactions.CommandContext):
    pass


@tv.subcommand(
    options=[
        interactions.Option(
            name="title",
            description="The title of the TV Show",
            required=True,
            type=interactions.OptionType.STRING,
        )
    ]
)
async def search(ctx: interactions.CommandContext, title: str):
    """Search for a title in SIMKL"""
    await ctx.defer()
    try:
        results = await searchSimkl(query=title, mediaType="tv")
        f = []
        so = []
        for r in results:
            rhel = r['year']
            f += [
                interactions.EmbedField(
                    name=r['title'],
                    value=f"*First aired on: {rhel}*",
                    inline=False
                )
            ]
            so += [
                interactions.SelectOption(
                    label=r['title'],
                    value=f"tv/{r['ids']['simkl_id']}",
                    description=f"First aired: {rhel}"
                )
            ]
        dcEm = generateSearchSelections(
            color=0x1F1F1F,
            homepage="https://simkl.com/",
            icon="https://media.discordapp.net/attachments/1078005713349115964/1094570318967865424/ico_square_1536x1536.png",
            platform="SIMKL",
            query=title,
            results=f,
            title="Search Results",
        )
        com = [
            interactions.SelectMenu(
                options=so,
                custom_id="simkl_search",
                placeholder="Select a TV Show to get more information"
            )
        ]

        await ctx.send("", embeds=dcEm, components=com)
        # timeout the selection
        await asyncio.sleep(90)
        await ctx.edit(MESSAGE_SELECT_TIMEOUT, embeds=dcEm, components=[])
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        await ctx.send("", embeds=dcEm)


@movie.subcommand(
    options=[
        interactions.Option(
            name="title",
            description="The title of the movie",
            required=True,
            type=interactions.OptionType.STRING,
        )
    ]
)
async def search(ctx: interactions.CommandContext, title: str):
    """Search for a title in SIMKL"""
    await ctx.defer()
    try:
        results = await searchSimkl(query=title, mediaType="movie")
        f = []
        so = []
        for r in results:
            rhel = r['year']
            ttl = r['title']
            f += [
                interactions.EmbedField(
                    name=ttl,
                    value=f"*Premiered on: {rhel}*",
                    inline=False
                )
            ]
            so += [
                interactions.SelectOption(
                    label=ttl,
                    value=f"movies/{r['ids']['simkl_id']}",
                    description=f"Premiered: {rhel}"
                )
            ]
        dcEm = generateSearchSelections(
            color=0x1F1F1F,
            homepage="https://simkl.com/",
            icon="https://media.discordapp.net/attachments/1078005713349115964/1094570318967865424/ico_square_1536x1536.png",
            platform="SIMKL",
            query=title,
            results=f,
            title="Search Results",
        )
        com = [
            interactions.SelectMenu(
                options=so,
                custom_id="simkl_search",
                placeholder="Select a movie to get more information"
            )
        ]

        await ctx.send("", embeds=dcEm, components=com)
        # timeout the selection
        await asyncio.sleep(90)
        await ctx.edit(MESSAGE_SELECT_TIMEOUT, embeds=dcEm, components=[])
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))
        await ctx.send("", embeds=dcEm)


@bot.component("simkl_search")
async def simkl_search(ctx: interactions.ComponentContext, choices: list[str]):
    await ctx.defer()
    ids = choices[0].split("/")
    mediaType = ids[0]
    simkl_id = ids[1]
    await simklSubmit(ctx=ctx, simkl_id=simkl_id, media=mediaType)


@tv.subcommand(
    options=[
        interactions.Option(
            name="simkl_id",
            description="The TV show id on SIMKL to fetch",
            required=True,
            type=interactions.OptionType.INTEGER,
        )
    ]
)
async def info(ctx: interactions.CommandContext, simkl_id: str):
    """Get TV show information from SIMKL using SIMKL ID"""

    await simklSubmit(ctx=ctx, simkl_id=simkl_id, media='tv')


@movie.subcommand(
    options=[
        interactions.Option(
            name="simkl_id",
            description="The movie id on SIMKL to fetch",
            required=True,
            type=interactions.OptionType.INTEGER,
        )
    ]
)
async def info(ctx: interactions.CommandContext, simkl_id: int):
    """Get movie information from SIMKL using SIMKL ID"""
    await ctx.defer()
    await simklSubmit(ctx=ctx, simkl_id=simkl_id, media='movies')

print("Starting bot...")

bot.start()
