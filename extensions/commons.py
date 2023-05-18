import csv
from datetime import datetime as dtime
from datetime import timezone as tz
from time import perf_counter as pc

import interactions as ipy

from modules.const import (
    AUTHOR_USERNAME,
    BOT_CLIENT_ID,
    BOT_SUPPORT_SERVER,
    database,
    gittyHash,
    gtHsh,
    ownerUserUrl,
)
from modules.i18n import fetch_language_data, read_user_language


class CommonCommands(ipy.Extension):
    """Common commands"""
    def __init__(self, bot: ipy.Client, now: dtime = dtime.now(tz=tz.utc)):
        """
        Initialize the extension

        Args:
            bot (ipy.Client): The bot client
            now (dtime, optional): The current time. Defaults to dtime.now(tz=tz.utc).
        """
        self.bot = bot
        self.now = now

    @ipy.slash_command(name="about", description="Get information about the bot")
    async def about(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["about"]
        embed = ipy.Embed(
            title=l_["header"],
            description=l_["text"].format(
                BOT_CLIENT_ID=BOT_CLIENT_ID,
                AUTHOR_USERNAME=AUTHOR_USERNAME,
                ownerUserUrl=ownerUserUrl,
                BOT_SUPPORT_SERVER=BOT_SUPPORT_SERVER,
                gtHsh=gtHsh,
                gittyHash=gittyHash,
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
    async def ping(self, ctx: ipy.SlashContext, defer: bool = False):
        start = pc()
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["ping"]
        langEnd = pc()
        if defer:
            await ctx.defer()  # to make sure if benchmark reflects other commands with .defer()
        send = await ctx.send(
            "",
            embed=ipy.Embed(
                title=l_["ping"]["title"],
                description=l_["ping"]["text"],
                color=0xDD2288,
            ),
        )
        ping = send.created_at.timestamp()
        pnow = dtime.now(tz=tz.utc).timestamp()
        end = pc()
        langPerfCount = (langEnd - start) * 1000
        pyPerfCount = (end - start) * 1000
        duration = (ping - pnow) * 1000
        duration = abs(duration)
        fields = [
            ipy.EmbedField(
                name="🤝 " + l_["websocket"]["title"],
                value=f"`{self.bot.latency * 1000:.2f}`ms\n> *{l_['websocket']['text']}*",
                inline=True,
            ),
            ipy.EmbedField(
                name="🤖 " + l_["bot"]["title"],
                value=f"`{duration:.2f}`ms\n> *{l_['bot']['text']}*",
                inline=True,
            ),
        ]
        readLat_start = pc()
        with open(database, "r", encoding="utf-8") as f:
            # skipcq: PYL-W0612
            reader = csv.reader(f, delimiter="\t")  # pyright: ignore
        readLat_end = pc()
        fields += [
            ipy.EmbedField(
                name="🔎 " + l_["dbRead"]["title"],
                value=f"`{(readLat_end - readLat_start) * 1000:.2f}`ms\n> *{l_['dbRead']['text']}*",
                inline=True,
            ),
            ipy.EmbedField(
                name="🌐 " + l_["langLoad"]["title"],
                value=f"`{langPerfCount:.2f}`ms\n> *{l_['langLoad']['text']}*",
                inline=True,
            ),
            ipy.EmbedField(
                name="🐍 " + l_["pyTime"]["title"],
                value=f"`{pyPerfCount:.2f}`ms\n> *{l_['pyTime']['text']}*",
                inline=True,
            ),
            ipy.EmbedField(
                name="📅 " + l_["uptime"]["title"],
                value=l_["uptime"]["text"].format(
                    TIMESTAMP=f"<t:{int(self.now.timestamp())}:R>"
                ),
                inline=True,
            ),
        ]
        await send.edit(
            content="",
            embed=ipy.Embed(
                title=l_["pong"]["title"],
                description=l_["pong"]["text"],
                color=0x996422,
                thumbnail=ipy.EmbedAttachment(
                    url="https://cdn.discordapp.com/attachments/1078005713349115964/1095771964783734874/main.png"
                ),
                fields=fields,
                footer=ipy.EmbedFooter(text=l_["pong"]["footer"]),
            ),
        )

    @ipy.slash_command(name="invite", description="Get the bot invite link")
    async def invite(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["invite"]
        invLink = f"https://discord.com/api/oauth2/authorize?client_id={BOT_CLIENT_ID}&permissions=274878221376&scope=bot%20applications.commands"
        dcEm = ipy.Embed(
            title=l_["title"],
            description=l_["text"].format(INVBUTTON=l_["buttons"]["invite"]),
            color=0x996422,
            fields=[
                ipy.EmbedField(
                    name=l_["fields"]["acc"]["title"],
                    value=l_["fields"]["acc"]["value"],
                    inline=True,
                ),
                ipy.EmbedField(
                    name=l_["fields"]["scope"]["title"],
                    value=l_["fields"]["scope"]["value"],
                    inline=True,
                ),
            ],
        )
        invButton = ipy.Button(
            label=l_["buttons"]["invite"],
            url=invLink,
            style=ipy.ButtonStyle.URL,
        )
        serverButton = ipy.Button(
            label=l_["buttons"]["support"],
            url=BOT_SUPPORT_SERVER,
            style=ipy.ButtonStyle.URL,
        )
        await ctx.send(embed=dcEm, components=[ipy.ActionRow(invButton, serverButton)])

    @ipy.slash_command(
        name="privacy", description="Get the bot's tl;dr version of privacy policy"
    )
    async def privacy(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["privacy"]
        butt = ipy.Button(
            label=l_["read"],
            url="https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md",
            style=ipy.ButtonStyle.URL,
        )
        em = ipy.Embed(
            title=l_["title"],
            description=l_["text"],
            color=0x996422,
        )
        await ctx.send(embed=em, components=[ipy.ActionRow(butt)])

    @ipy.slash_command(
        name="support", description="Give (financial) support to the bot"
    )
    async def support(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_ = fetch_language_data(ul)["support"]
        txt: str = l_["text"]
        em = ipy.Embed(
            title=l_["title"],
            description=txt.format(
                KOFI="https://ko-fi.com/nattadasu",
                PAYPAL="https://paypal.me/nattadasu",
                PATREON="https://www.patreon.com/nattadasu",
                GHSPONSOR="https://github.com/sponsors/nattadasu",
                SAWERIA="https://saweria.co/nattadasu",
                TRAKTEER="https://trakteer.id/nattadasu",
                GHREPO="https://github.com/nattadasu/ryuuRyuusei",
                SUPPORT=BOT_SUPPORT_SERVER,
            ),
            color=0x996422,
        )
        await ctx.send(embed=em)


def setup(bot, now):
    CommonCommands(bot, now)
