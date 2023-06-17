import interactions as ipy

from classes.i18n import LanguageDict
from modules.commons import generate_commons_except_embed
from modules.discord import generate_discord_profile_embed
from modules.i18n import fetch_language_data, read_user_language


class Profile(ipy.Extension):
    """Profile commands"""

    profile = ipy.SlashCommand(
        name="profile",
        description="Get your profile information from various platforms",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5,
        ),
    )

    @profile.subcommand(
        sub_cmd_name="discord",
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
    async def profile_discord(
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
                lang_dict=l_,
            )
            await ctx.send(embed=embed)


def setup(bot):
    Profile(bot)
