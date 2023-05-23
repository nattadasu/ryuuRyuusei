from datetime import datetime, timezone

import interactions as ipy

from classes.database import UserDatabase


class WhoAmI(ipy.Extension):
    """Extension class for /whoami"""

    def __init__(self, bot: ipy.AutoShardedClient):
        self.bot = bot

    @ipy.slash_command(name="whoami", description="Interactively read your data")
    async def whoami(self, ctx: ipy.SlashContext):
        await ctx.defer(ephemeral=True)

        async with UserDatabase() as ud:
            resp = await ud.check_if_registered(ctx.author.id)

        if resp is False:
            await ctx.send("You are not registered!")
            return
        else:
            async with UserDatabase() as ud:
                resp = await ud.get_user_data(ctx.author.id)

        embed: ipy.Embed = ipy.Embed(
            author=ipy.EmbedAuthor(
                name=f"Who am I?",
                icon_url=ctx.author.avatar.url,
            ),
            title=f"{ctx.author.username}",
            fields=[
                ipy.EmbedField(
                    name="Discord",
                    value="Below is your Discord data",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Username",
                    value=ctx.author.username,
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Display Name*",
                    value=ctx.author.display_name,
                    inline=True,
                ),
                ipy.EmbedField(
                    name="User ID",
                    value=f"`{ctx.author.id}`",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Created at",
                    value=f"<t:{int(ctx.author.created_at.timestamp())}:F>",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Database",
                    value="Below is your database data",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Registered at",
                    value=f"<t:{int(resp.registered_at.timestamp())}:F>",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Registered Server ID",
                    value=f"`{resp.registered_guild}`",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Registered by",
                    value=f"Yourself" if resp.registered_by == ctx.author.id else f"<@{resp.registered_by}>",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="MyAnimeList",
                    value="Below is your MyAnimeList data",
                    inline=False,
                ),
                ipy.EmbedField(
                    name="Username",
                    value=f"{resp.mal_username}" if resp.mal_username is not None else f"*Removed*",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="User ID",
                    value=f"`{resp.mal_id}`",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Joined at",
                    value=f"<t:{int(resp.mal_joined.timestamp())}:F>",
                    inline=True,
                ),
            ],
            color=ctx.author.accent_color,
            footer=ipy.EmbedFooter(
                text="* Not saved in database"
            ),
            timestamp=datetime.now(tz=timezone.utc)
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_image(url=ctx.author.banner.url)
        await ctx.send(embed=embed)


def setup(bot: ipy.AutoShardedClient):
    """Load the extension"""
    WhoAmI(bot)
