import interactions as ipy

from classes.i18n import LanguageDict
from modules.commons import (generate_commons_except_embed,
                             save_traceback_to_file)
from modules.discord import generate_discord_profile_embed
from modules.i18n import fetch_language_data, read_user_language


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
        ul = read_user_language(ctx)
        l_: LanguageDict = fetch_language_data(ul, use_raw=True)
        try:
            embed = await generate_discord_profile_embed(
                bot=self.bot,
                l_=l_,
                ctx=ctx,
                user=user,
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = generate_commons_except_embed(
                description=l_["strings"]["profile"]["exception"]["general"],
                error=f"{e}",
                language=l_,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("discord_profile", ctx.author, e)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    DiscordCog(bot)
