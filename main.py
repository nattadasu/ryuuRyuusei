import asyncio
import csv
from datetime import datetime as dtime
from datetime import timezone as tz
from time import perf_counter as pc

import interactions as ipy

from modules.commons import *
from modules.const import *
from modules.i18n import lang, paginateLanguage, readUserLang, setLanguage
from modules.myanimelist import searchMalAnime
from modules.nekomimidb import nekomimiSubmit

now: dtime = dtime.now(tz=tz.utc)

bot = ipy.Client(
    token=BOT_TOKEN,
    status=ipy.Status.IDLE,
    auto_defer=ipy.AutoDefer(
        enabled=True,
        time_until_defer=1.5,
    ),
    activity=ipy.Activity(
        name="Kagamine Len's Live Concert",
        type=ipy.ActivityType.WATCHING,
    )
)


@ipy.slash_command(name="about", description="Get information about the bot")
async def about(ctx: ipy.SlashContext):
    """Get information about the bot"""
    ul = readUserLang(ctx)
    l_ = lang(ul)['about']
    embed = ipy.Embed(
        title=l_["header"],
        description=l_["text"].format(
            BOT_CLIENT_ID=BOT_CLIENT_ID,
            AUTHOR_USERNAME=AUTHOR_USERNAME,
            ownerUserUrl=ownerUserUrl,
            BOT_SUPPORT_SERVER=BOT_SUPPORT_SERVER,
            gtHsh=gtHsh,
            gittyHash=gittyHash
        ),
        color=0x996422,
    )
    await ctx.send(embed=embed)


@ipy.slash_command(name="ping", description="Ping the bot")
@ipy.slash_option(
    name="defer",
    description="Defer the command",
    opt_type=ipy.OptionType.BOOLEAN,
    required=False,
)
async def ping(ctx: ipy.SlashContext, defer: bool = False):
    start = pc()
    ul = readUserLang(ctx)
    l_ = lang(ul)['ping']
    langEnd = pc()
    if defer:
        await ctx.defer()  # to make sure if benchmark reflects other commands with .defer()
    send = await ctx.send(
        "",
        embed=ipy.Embed(
            title=l_['ping']['title'],
            description=l_['ping']['text'],
            color=0xDD2288,
        ))
    ping = send.created_at.timestamp()
    pnow = dtime.now(tz=tz.utc).timestamp()
    end = pc()
    langPerfCount = (langEnd - start) * 1000
    pyPerfCount = (end - start) * 1000
    duration = (ping - pnow) * 1000
    duration = abs(duration)
    fields = [
        ipy.EmbedField(
            name="🤖 " + l_['bot']['title'],
            value=f"`{duration:.2f}`ms\n> *{l_['bot']['text']}*",
            inline=True,
        ),
        ipy.EmbedField(
            name="🤝 " + l_['websocket']['title'],
            value=f"`{bot.latency * 1000:.2f}`ms\n> *{l_['websocket']['text']}*",
            inline=True,
        ),
    ]
    readLat_start = pc()
    with open(database, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        del reader
    readLat_end = pc()
    fields += [
        ipy.EmbedField(
            name="🔎 " + l_['dbRead']['title'],
            value=f"`{(readLat_end - readLat_start) * 1000:.2f}`ms\n> *{l_['dbRead']['text']}*",
            inline=True,
        ),
        ipy.EmbedField(
            name="🌐 " + l_['langLoad']['title'],
            value=f"`{langPerfCount:.2f}`ms\n> *{l_['langLoad']['text']}*",
            inline=True,
        ),
        ipy.EmbedField(
            name="🐍 " + l_['pyTime']['title'],
            value=f"`{pyPerfCount:.2f}`ms\n> *{l_['pyTime']['text']}*",
            inline=True,
        ),
        ipy.EmbedField(
            name="📅 " + l_['uptime']['title'],
            value=l_['uptime']['text'].format(
                TIMESTAMP=f"<t:{int(now.timestamp())}:R>"),
            inline=True,
        )
    ]
    await send.edit(content="", embed=ipy.Embed(
        title=l_['pong']['title'],
        description=l_['pong']['text'],
        color=0x996422,
        thumbnail=ipy.EmbedAttachment(
            url="https://cdn.discordapp.com/attachments/1078005713349115964/1095771964783734874/main.png"
        ),
        fields=fields,
        footer=ipy.EmbedFooter(
            text=l_['pong']['footer']
        )
    ))


@ipy.slash_command(name="invite", description="Get the bot invite link")
async def invite(ctx: ipy.SlashContext):
    """Get bot invite link"""
    ul = readUserLang(ctx)
    l_ = lang(ul)['invite']
    invLink = f"https://discord.com/api/oauth2/authorize?client_id={BOT_CLIENT_ID}&permissions=274878221376&scope=bot%20applications.commands"
    dcEm = ipy.Embed(
        title=l_['title'],
        description=l_['text'].format(INVBUTTON=l_['buttons']['invite']),
        color=0x996422,
        fields=[
            ipy.EmbedField(
                name=l_['fields']['acc']['title'],
                value=l_['fields']['acc']['value'],
                inline=True
            ),
            ipy.EmbedField(
                name=l_['fields']['scope']['title'],
                value=l_['fields']['scope']['value'],
                inline=True
            ),
        ]
    )
    invButton = ipy.Button(
        label=l_['buttons']['invite'],
        url=invLink,
        style=ipy.ButtonStyle.URL,
    )
    serverButton = ipy.Button(
        label=l_['buttons']['support'],
        url=BOT_SUPPORT_SERVER,
        style=ipy.ButtonStyle.URL,
    )
    await ctx.send(embed=dcEm, components=[ipy.ActionRow(invButton, serverButton)])


@ipy.slash_command(name="privacy", description="Get the bot's tl;dr version of privacy policy")
async def privacy(ctx: ipy.SlashContext):
    ul = readUserLang(ctx)
    l_ = lang(ul)['privacy']
    butt = ipy.Button(
        label=l_['read'],
        url="https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md",
        style=ipy.ButtonStyle.URL,
    )
    em = ipy.Embed(
        title=l_['title'],
        description=l_['text'],
        color=0x996422,
    )
    await ctx.send(embed=em, components=[ipy.ActionRow(butt)])


@ipy.slash_command(name="support", description="Give (financial) support to the bot")
async def support(ctx: ipy.SlashContext):
    ul = readUserLang(ctx)
    l_ = lang(ul)['support']
    txt: str = l_['text']
    em = ipy.Embed(
        title=l_['title'],
        description=txt.format(
            KOFI="https://ko-fi.com/nattadasu",
            PAYPAL="https://paypal.me/nattadasu",
            PATREON="https://www.patreon.com/nattadasu",
            GHSPONSOR="https://github.com/sponsors/nattadasu",
            SAWERIA="https://saweria.co/nattadasu",
            TRAKTEER="https://trakteer.id/nattadasu",
            GHREPO="https://github.com/nattadasu/ryuuRyuusei",
            SUPPORT=BOT_SUPPORT_SERVER
        ),
        color=0x996422,
    )
    await ctx.send(embed=em)


@ipy.slash_command(
    name="anime",
    description="Get anime information from MyAnimeList",
)
async def anime(ctx: ipy.SlashContext):
    pass


@anime.subcommand(
    sub_cmd_name="search",
    sub_cmd_description="Search for anime",
    options=[
        ipy.SlashCommandOption(
            name="query",
            description="The anime title to search for",
            type=ipy.OptionType.STRING,
            required=True
        )
    ]
)
async def anime_search(ctx: ipy.SlashContext, query: str):
    await ctx.defer()
    ul = readUserLang(ctx)
    l_ = lang(ul, useRaw=True)
    send = await ctx.send(embed=ipy.Embed(
        title=l_['commons']['search']['init_title'],
        description=l_['commons']['search']['init'].format(
            QUERY=query,
            PLATFORM="MyAnimeList",
        ),
    ))
    f = []
    so = []
    try:
        res = await searchMalAnime(title=query)
        if res is None or len(res) == 0:
            raise Exception("No result")
        for a in res:
            a = a['node']
            if a['start_season'] is None:
                a['start_season'] = {'season': 'Unknown', 'year': 'Year'}
            media_type: str = a['media_type'].lower()
            try:
                media_type = l_['commons']['media_formats'][media_type]
            except KeyError:
                media_type = l_['commons']['unknown']
            season: str = a['start_season']['season'].title()
            year = a['start_season']['year']
            title = a['title']
            mdTitle = sanitizeMarkdown(title)
            alt = a['alternative_titles']
            if alt is not None and alt['ja'] is not None:
                native = sanitizeMarkdown(alt['ja'])
                native += "\n"
            else:
                native = ""
            f += [
                ipy.EmbedField(
                    name=mdTitle,
                    value=f"{native}`{a['id']}`, {media_type}, {season} {year}",
                    inline=False
                )
            ]
            so += [
                ipy.StringSelectOption(
                    # trim to 80 chars in total
                    label=title[:80],
                    value=a['id'],
                    description=f"{media_type}, {season} {year}"
                )
            ]
        if len(f) >= 1:
            result = generateSearchSelections(
                title=l_['commons']['search']['result_title'].format(QUERY=query),
                language=ul,
                mediaType="anime",
                query=query,
                platform="MyAnimeList",
                homepage="https://myanimelist.net",
                results=f,
                icon="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png",
                color=0x2F51A3,
            )
            await send.edit(
                content="",
                embed=result,
                components=ipy.ActionRow(
                    ipy.StringSelectMenu(
                        *so,
                        placeholder="Choose an anime",
                        custom_id="mal_search"
                    )
                )
            )
        await asyncio.sleep(60)
        await send.edit(components=[])
    except:
        l_ = l_['strings']['anime']['search']['exception']
        emoji = rSub(r"(<:.*:)(\d+)(>)", r"\2", EMOJI_UNEXPECTED_ERROR)
        await send.edit(content="", embed=ipy.Embed(
            title=l_['title'],
            description=l_['text'],
            color=0xFF0000,
            footer=ipy.EmbedFooter(
                text=l_['footer']
            ),
            thumbnail=ipy.EmbedThumbnail(
                url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1"
            ),
        ))


@ipy.slash_command(
    name="random",
    description="Get a random stuff",
)
async def random(ctx: ipy.SlashContext):
    pass


@random.subcommand(
    group_name="nekomimi",
    group_description="Get a random character in cat ears",
    sub_cmd_name="boy",
    sub_cmd_description="Get an image of boy character in cat ears",
)
async def random_nekomimi_boy(ctx: ipy.SlashContext):
    await ctx.defer()
    ul = readUserLang(ctx)
    l_ = lang(ul)['random']['nekomimi']
    await nekomimiSubmit(ctx=ctx, gender='boy', lang=l_)


@random.subcommand(
    group_name="nekomimi",
    group_description="Get a random character in cat ears",
    sub_cmd_name="girl",
    sub_cmd_description="Get an image of girl character in cat ears",
)
async def random_nekomimi_girl(ctx: ipy.SlashContext):
    await ctx.defer()
    ul = readUserLang(ctx)
    l_ = lang(ul)['random']['nekomimi']
    await nekomimiSubmit(ctx=ctx, gender='girl', lang=l_)


@random.subcommand(
    group_name="nekomimi",
    group_description="Get a random character in cat ears",
    sub_cmd_name="randomize",
    sub_cmd_description="Get an image of random character of any gender in cat ears",
)
async def random_nekomimi_randomize(ctx: ipy.SlashContext):
    await ctx.defer()
    ul = readUserLang(ctx)
    l_ = lang(ul)['random']['nekomimi']
    await nekomimiSubmit(ctx=ctx, lang=l_)


@ipy.slash_command(
    name="usersettings",
    description="Change the bot settings",
)
async def usersettings(ctx: ipy.InteractionContext):
    pass


@usersettings.subcommand(
    group_name="language",
    group_description="Change the bot language",
    sub_cmd_name="list",
    sub_cmd_description="List the available languages",
)
async def usersettings_language_list(ctx: ipy.InteractionContext):
    await paginateLanguage(bot=bot, ctx=ctx)


@usersettings.subcommand(
    group_name="language",
    group_description="Change the bot language",
    sub_cmd_name="set",
    sub_cmd_description="Set the bot language",
)
@ipy.slash_option(
    name="code",
    description="Language code",
    required=True,
    opt_type=ipy.OptionType.STRING,
)
async def usersettings_language_set(ctx: ipy.InteractionContext, code: str):
    try:
        await setLanguage(code=code, ctx=ctx, isGuild=False)
        await ctx.send(f"{EMOJI_SUCCESS} Language set to {code}", ephemeral=True)
    except Exception as e:
        await ctx.send(f"{EMOJI_FORBIDDEN} {e}")


@ipy.slash_command(
    name="serversettings",
    description="Change the bot settings",
    default_member_permissions=ipy.Permissions.ADMINISTRATOR,
    dm_permission=False,
)
async def serversettings(ctx: ipy.InteractionContext):
    pass


@serversettings.subcommand(
    group_name="language",
    group_description="Change the bot language",
    sub_cmd_name="server",
    sub_cmd_description="Set the bot language for this server",
)
@ipy.slash_option(
    name="code",
    description="Language code, check from /usersettings language list",
    required=True,
    opt_type=ipy.OptionType.STRING,
)
async def serversettings_language_set(ctx: ipy.InteractionContext, code: str):
    try:
        await setLanguage(code=code, ctx=ctx, isGuild=True)
        await ctx.send(f"{EMOJI_SUCCESS} Server Language set to {code}")
    except Exception as e:
        await ctx.send(f"{EMOJI_FORBIDDEN} {e}")


async def main():
    """Main function"""
    bot.load_extension('interactions.ext.sentry',
                       token=SENTRY_DSN)
    bot.load_extension("interactions.ext.jurigged")
    bot.del_unused_app_cmd = True
    bot.sync_interactions = True
    bot.send_command_tracebacks = False
    bot.sync_ext = True
    await bot.astart()


if __name__ == "__main__":
    print("Starting bot...")
    print("Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
    bot_run = pc()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_stop = pc()
        print("Bot stopped by user.")
        now: dtime = dtime.now(tz=tz.utc)
        print("Date: " + now.strftime("%d/%m/%Y %H:%M:%S"))
        print("Uptime: " + str(int(bot_stop - bot_run)) +
              "s, or around " + str(int((bot_stop - bot_run) / 60)) + "m")
