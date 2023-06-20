import csv
import re
from datetime import datetime as dtime
from datetime import timezone as tz
from time import perf_counter as pc

import interactions as ipy
from aiohttp import __version__ as aiohttp_version

from classes.i18n import LanguageDict
from modules.const import (AUTHOR_USERNAME, BOT_CLIENT_ID, BOT_SUPPORT_SERVER,
                           EMOJI_SUCCESS, USER_AGENT, database, gittyHash,
                           gtHsh, ownerUserUrl)
from modules.i18n import fetch_language_data, read_user_language


class CommonCommands(ipy.Extension):
    """Common commands"""

    def __init__(
            self,
            bot: ipy.AutoShardedClient,
            now: dtime = dtime.now(
            tz=tz.utc)):
        """
        Initialize the extension

        Args:
            bot (ipy.AutoShardedClient): The bot client
            now (dtime, optional): The current time. Defaults to dtime.now(tz=tz.utc).
        """
        self.bot = bot
        self.now = now

    @ipy.cooldown(ipy.Buckets.GUILD, 1, 60)
    @ipy.slash_command(name="about",
                       description="Get information about the bot")
    async def about(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["about"]
        authors = ""
        for u in self.bot.owners:
            authors += f"* {u.username} (<@!{u.id}>)\n"
        embed = ipy.Embed(
            title="About",
            description=l_["text"].format(
                BOT_CLIENT_ID=BOT_CLIENT_ID,
                AUTHOR_USERNAME=AUTHOR_USERNAME,
                ownerUserUrl=ownerUserUrl,
                BOT_SUPPORT_SERVER=BOT_SUPPORT_SERVER,
                gtHsh=gtHsh,
                gittyHash=gittyHash,
            ),
            fields=[
                ipy.EmbedField(
                    name="User Agent",
                    value=f'```http\nUser-Agent: "{USER_AGENT}"\n```',
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Interactions.py Version",
                    value=f"```py\n{ipy.__version__}\n```",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Aiohttp Version",
                    value=f"```py\n{aiohttp_version}\n```",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Python Version",
                    value=f"```py\n{ipy.__py_version__}\n```",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Bot Author",
                    value=f"{authors}",
                    inline=False,
                ),
            ],
            color=0x996422,
        )
        embed.set_thumbnail(self.bot.user.avatar.url)
        embed.set_footer(text="To get uptime and other info, use /ping")
        await ctx.send(embed=embed)

    @ipy.cooldown(ipy.Buckets.GUILD, 1, 5)
    @ipy.slash_command(name="ping", description="Ping the bot")
    async def ping(self, ctx: ipy.SlashContext):
        start = pc()
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["ping"]
        langEnd = pc()
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
                    TIMESTAMP=f"<t:{int(self.now.timestamp())}:R>"),
                inline=True,
            ),
        ]
        embed = ipy.Embed(
            title=l_["pong"]["title"],
            description=l_["pong"]["text"],
            color=0x996422,
            fields=fields,
        )
        emoji = re.sub(r"<:[a-zA-Z0-9_]+:([0-9]+)>", r"\1", EMOJI_SUCCESS)
        embed.set_thumbnail(
            url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")
        await send.edit(
            embed=embed,
        )

    @ipy.cooldown(ipy.Buckets.USER, 1, 60)
    @ipy.slash_command(name="invite", description="Get the bot invite link")
    async def invite(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["invite"]
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
        await ctx.send(
            embed=dcEm,
            components=[ipy.ActionRow(invButton, serverButton)],
            ephemeral=True,
        )

    @ipy.cooldown(ipy.Buckets.GUILD, 1, 60)
    @ipy.slash_command(name="privacy",
                       description="Get the bot's tl;dr version of privacy policy")
    async def privacy(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["privacy"]
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

    @ipy.cooldown(ipy.Buckets.GUILD, 1, 60)
    @ipy.slash_command(
        name="support", description="Give (financial) support to the bot"
    )
    async def support(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul)["strings"]["support"]
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
