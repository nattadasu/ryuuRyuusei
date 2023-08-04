import csv
import re
from datetime import datetime as dtime
from datetime import timezone as tz
from time import perf_counter as pc
from typing import Any

import interactions as ipy
from aiohttp import __version__ as aiohttp_version

from modules.const import (AUTHOR_USERNAME, BOT_CLIENT_ID, BOT_SUPPORT_SERVER,
                           DATABASE_PATH, EMOJI_SUCCESS, USER_AGENT, GIT_COMMIT_HASH,
                           GT_HSH, AUTHOR_USER_URL)
from modules.i18n import fetch_language_data, read_user_language


class CommonCommands(ipy.Extension):
    """Common commands"""

    def __init__(
            self,
            bot: ipy.Client | ipy.AutoShardedClient,
            now: dtime = dtime.now(tz=tz.utc)):
        """
        Initialize the extension

        Args:
            bot (ipy.Client | ipy.AutoShardedClient): The bot client
            now (dtime, optional): The current time. Defaults to dtime.now(tz=tz.utc).
        """
        self.bot = bot
        self.now = now

    @ipy.cooldown(ipy.Buckets.GUILD, 1, 60)
    @ipy.slash_command(name="about",
                       description="Get information about the bot")
    async def about(self, ctx: ipy.SlashContext):
        authors = ""
        for u in self.bot.owners:
            authors += f"* {u.username} (<@!{u.id}>)\n"
        embed = ipy.Embed(
            title="About",
            description=f"""{self.bot.user.mention} is a rolling release Discord bot that uses interactions.py and Python to offer a variety of features and commands for Discord users. You can look up your profile from Discord, AniList, Shikimori, MyAnimeList, and Last.fm and customize your summary for each platform. You can also search for anime, manga, games, TV shows, and movies from platforms like MyAnimeList, AniList, SIMKL, Spotify, and more. You can also export your data in different formats and enjoy true randomness with some commands. 🚀

The bot cares about your privacy by not storing any data on its server except for essential information. You can also delete your data anytime using the /unregister command. For more details, you can read the Privacy Policy. 🔒

The bot has many commands for different purposes, such as anime, manga, game, TV show, movie, music, and external link lookups. You can also access profile lookup commands, data control commands, settings commands (for both users and servers), randomization commands, and utility commands.

If you want to contact the author, send a DM to [{AUTHOR_USERNAME}]({AUTHOR_USER_URL}) or via [support server]({BOT_SUPPORT_SERVER}).""",
            color=0x996422,
        )
        embed.add_fields(
            ipy.EmbedField(
                name="Bot ID",
                value=f"`{self.bot.user.id}`",
                inline=True,
            ),
            ipy.EmbedField(
                name="Bot Version",
                value=f"[{GT_HSH}](https://github.com/nattadasu/ryuuRyuusei/commit/{GIT_COMMIT_HASH})",
                inline=True,
            ),
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
        )
        embed.set_thumbnail(self.bot.user.avatar.url)
        embed.set_footer(text="To get uptime and other info, use /ping")
        await ctx.send(embed=embed)

    @ipy.cooldown(ipy.Buckets.GUILD, 1, 5)
    @ipy.slash_command(name="ping", description="Ping the bot")
    async def ping(self, ctx: ipy.SlashContext):
        start = pc()
        ul = read_user_language(ctx)
        l_: dict[str, Any] = fetch_language_data(ul)["strings"]["ping"]
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
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            # skipcq: PYL-W0612
            reader = csv.reader(f, delimiter="\t")  # pyright: ignore
        readLat_end = pc()
        # uptime = dtime.now(tz=tz.utc) - self.bot.start_time
        # uptime_epoch = uptime.total_seconds()
        uptime_epoch = self.now.timestamp()
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
                    TIMESTAMP=f"<t:{int(uptime_epoch)}:R>"),
                inline=True,
            ),
        ]
        embed = ipy.Embed(
            title=l_["pong"]["title"],
            description=l_["pong"]["text"],
            color=0x996422,
        )
        embed.add_fields(*fields)
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
        l_: dict[str, Any] = fetch_language_data(ul)["strings"]["invite"]
        invLink = f"https://discord.com/api/oauth2/authorize?client_id={BOT_CLIENT_ID}&permissions=274878221376&scope=bot%20applications.commands"
        dcEm = ipy.Embed(
            title=l_["title"],
            description=l_["text"].format(INVBUTTON=l_["buttons"]["invite"]),
            color=0x996422,
        )
        dcEm.add_fields(
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
        butt = ipy.Button(
            label="Read the full version",
            url="https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md",
            style=ipy.ButtonStyle.URL,
        )
        em = ipy.Embed(
            title="Privacy Policy",
            description="""# Privacy Policy, tl;dr version
Hello and thank you for your interest to read this tl;dr version of Privacy Policy.

In this message we shortly briefing which content we collect, store, and
use, including what third party services we used for bot to function as expected. You can read the full version of [Privacy Policy here at anytime you wish](https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md).
## What we collect
We collect personal information tied about you, with your consent, the following data:
* AniList (optional): username, user ID
* Discord: username, discriminator, user snowflake ID, joined date, guild/server ID of registration, server name, date of registration, user referral (if any)
* Last.FM (optional): username
* MyAnimeList: username, user ID, joined date
* Shikimori (optional): username, user ID
* User's settings (optional): language, autoembed
## What we share about you
We share limited personal information about you and/or other, required for the bot to function as expected, with the following services:
* AniList: AniList Username
* Discord: Message Author Identifier
* Last.FM: Last.FM Username
* MAL-Heatmap: MyAnimeList Username
* MyAnimeList (via Jikan): MyAnimeList Username
* PronounDB: Message Author Identifier
* Shikimori: Shikimori Username
## Which data we share aggregated
We share aggregated and anonymized data to 3rd parties. We may share aggregated and anonymized data to third parties for the purpose of improving our services and statistics. This data is not personally identifiable and is used for statistical purposes only.
## About caching
We stores cache in our system for limited time. This cache is used to improve the performance of the bot and to reduce the load on the third party services. The cache is stored for a limited time and is automatically deleted after a certain period of time.
## About logging
We do not collect, store, or use any logs of messages sent by system about you under any circumstances. We delete the log generated by the system periodically for bug fixing and performance improvement purposes.
## About data retention
We retain your personal information only for as long as necessary to provide you with our services and as described in our Privacy Policy.
## About user rights of data subject
By default, Ryuuzaki Ryuusei enforces EU General Data Protection Regulation (GDPR), the California Consumer Privacy Act (CCPA), and the Personal Data Protection Act of Indonesia (UU PDP) compliance for all its users, regardless of their location or geographical boundaries. These data protection regulations apply globally, without limitation of place, ensuring that every user's personal data is treated with the same level of respect and protection, regardless of where they reside.

In short, you have the following rights:
Opt-out; Non-discrimination; Access, know, and portability of personal data; Modify, rectify, delete, and restrict; Limit; Stop processing; Notify; Withdraw consent; Object to automated decision; and Receive personal data in common format

We highly suggest to read the full version of [Privacy Policy here](https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md) for more information.""",
            color=0x996422,
        )
        await ctx.send(embed=em, components=[ipy.ActionRow(butt)], ephemeral=True)

    @ipy.cooldown(ipy.Buckets.GUILD, 1, 60)
    @ipy.slash_command(
        name="support", description="Give (financial) support to the bot"
    )
    async def support(self, ctx: ipy.SlashContext):
        ul = read_user_language(ctx)
        l_: dict[str, Any] = fetch_language_data(ul)["strings"]["support"]
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


def setup(bot: ipy.Client | ipy.AutoShardedClient, now: dtime):
    CommonCommands(bot, now)
