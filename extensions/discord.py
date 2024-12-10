from datetime import timezone
from typing import Any, Literal

import interactions as ipy

from classes.userpfp import UserPFP
from classes.usrbg import UsrBg
from modules.commons import (
    generate_commons_except_embed,
    generate_utils_except_embed,
    save_traceback_to_file,
)
from modules.discord import generate_discord_profile_embed

GIF_ISSUE = (
    "Image might be outdated because cache or it's actually a GIF/animated image"
)


class DiscordCog(ipy.Extension):
    """Extension for interacting with Discord"""

    discord_head = ipy.SlashCommand(
        name="discord",
        description="Get your profile information from Discord",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5,
        ),
    )

    @discord_head.subcommand(
        sub_cmd_name="profile",
        sub_cmd_description="Get your Discord profile information",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to get profile information of",
                type=ipy.OptionType.USER,
                required=False,
            )
        ],
    )
    async def discord_profile(
        self, ctx: ipy.SlashContext, user: ipy.User | ipy.Member | None = None
    ):
        await ctx.defer()
        try:
            embed = await generate_discord_profile_embed(
                bot=self.bot,  # type: ignore
                ctx=ctx,
                user=user,
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = generate_commons_except_embed(
                description="An error occurred while getting information about the user",
                error=f"{e}",
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("discord_profile", ctx.author, e)

    @discord_head.subcommand(
        sub_cmd_name="banner",
        sub_cmd_description="Fetch user's banner",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="The user to fetch the banner from",
                required=False,
                type=ipy.OptionType.USER,
            ),
            ipy.SlashCommandOption(
                name="scope",
                description="Whether to fetch the banner from the user or usrbg",
                required=False,
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Discord Profile (Default)", value="user"
                    ),
                    ipy.SlashCommandChoice(name="UsrBG", value="usrbg"),
                ],
            ),
        ],
    )
    async def discord_banner(
        self,
        ctx: ipy.SlashContext,
        user: ipy.User | ipy.Member | None = None,
        scope: str = "user",
    ):
        await ctx.defer()

        if not user:
            user = ctx.author

        udata: dict[str, Any] = await self.bot.http.get_user(user.id)  # type: ignore
        udict = ipy.User.from_dict(udata, self.bot)  # type: ignore

        if scope == "usrbg":
            try:
                async with UsrBg() as usrbg:
                    banner = await usrbg.get_background(user.id)
            except Exception as _:
                banner = None
        else:
            try:
                banner = udict.banner.url if udict.banner else None
                banner = None if "None" in banner else banner  # type: ignore
            except Exception as _:
                banner = None

        source = "Global" if scope == "user" else "UsrBG"
        if not banner:
            embed = generate_commons_except_embed(
                description=f"{user.mention} does not have a banner set",
                error="No banner found",
            )
            await ctx.send(embed=embed)
            return

        embed = ipy.Embed(
            title=f"{user.display_name}'s {source} banner",
            color=udict.accent_color.value if udict.accent_color else 0x000000,
            timestamp=ipy.Timestamp.now(tz=timezone.utc),
        )
        embed.set_image(url=banner)
        embed.set_thumbnail(url=user.display_avatar.url)
        if scope == "usrbg":
            embed.set_footer(GIF_ISSUE)
        embed.add_field(name="User", value=f"```{user}```", inline=True)
        embed.add_field(name="Direct Link", value=banner, inline=True)
        await ctx.send(embed=embed)

    @discord_head.subcommand(
        sub_cmd_name="avatar",
        sub_cmd_description="Fetch user's avatar",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="The user to fetch the avatar from",
                required=False,
                type=ipy.OptionType.USER,
            ),
            ipy.SlashCommandOption(
                name="scope",
                description="Whether to fetch the avatar from the global profile or server profile",
                required=False,
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Discord Profile (Default)", value="user"
                    ),
                    ipy.SlashCommandChoice(name="Server Profile", value="server"),
                    ipy.SlashCommandChoice(name="UserPFP", value="userpfp"),
                ],
            ),
        ],
    )
    async def utilities_avatar(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member | ipy.User | None = None,
        scope: Literal["user", "server", "userpfp"] = "user",
    ):
        await ctx.defer()

        if not user:
            user = ctx.author

        avatar = None

        match scope:
            case "user":
                avatar = user.avatar.url
            case "server":
                avatar = user.display_avatar.url
            case "userpfp":
                async with UserPFP() as pfp:
                    avatar = await pfp.get_picture(user.id)

        if not avatar:
            embed = generate_utils_except_embed(
                description="Failed to fetch the avatar",
                field_name="User",
                field_value=f"```{user}```",
                error="User has no avatar",
            )
            await ctx.send(embed=embed)
            return

        embed = ipy.Embed(
            title=f"{user.display_name}'s avatar",
            color=0x566A82,
            timestamp=ipy.Timestamp.now(tz=timezone.utc),
        )
        embed.set_image(url=avatar)
        embed.add_field(name="User", value=f"```{user}```", inline=True)
        embed.add_field(name="Direct Link", value=avatar, inline=True)
        if scope == "userpfp":
            embed.set_footer(GIF_ISSUE)
        await ctx.send(embed=embed)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    DiscordCog(bot)
