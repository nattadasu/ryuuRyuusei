import interactions as ipy

from classes.database import UserDatabase
from modules.discord import generate_discord_profile_embed
from extensions.birthday import generate_birthday_embed


class WhoAmI(ipy.Extension):
    """Extension class for /whoami"""

    @ipy.cooldown(ipy.Buckets.USER, 1, 10)
    @ipy.slash_command(name="whoami", description="Interactively read your data")
    async def whoami(self, ctx: ipy.SlashContext):
        await ctx.defer(ephemeral=True)

        async with UserDatabase() as ud:
            resp = await ud.check_if_registered(ctx.author.id)

        if resp is False:
            await ctx.send("You are not registered!")
            return
        async with UserDatabase() as ud:
            resp = await ud.get_user_data(ctx.author.id)

        discord_embed = await generate_discord_profile_embed(
            bot=self.bot,
            ctx=ctx,
            user=ctx.author,
        )

        database_embed = ipy.Embed(
            title="Database Data",
            description="Below is your database data",
            color=ctx.author.accent_color,
            timestamp=ipy.Timestamp.fromtimestamp(resp.registered_at.timestamp()),
        )
        database_embed.add_fields(
            *[
                ipy.EmbedField(
                    name="Registered at",
                    value=f"<t:{int(resp.registered_at.timestamp())}:F>",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Registered Server ID",
                    value=f"`{resp.registered_guild_id}`",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Registered Server Name",
                    value=resp.registered_guild_name or "*None*",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Registered by",
                    value="Yourself"
                    if resp.registered_by == ctx.author.id
                    else f"<@{resp.registered_by}>",
                    inline=True,
                ),
            ]
        )
        database_embed.set_thumbnail(
            url="https://3.bp.blogspot.com/-V4IWtEE4mi0/U2sr28tExOI/AAAAAAAAf50/ivdH5uLVwUc/s800/computer_harddisk.png"
        )

        mal_embed = ipy.Embed(
            title="MyAnimeList Data",
            description="Below is your MyAnimeList data",
            color=0x2E51A2,
            timestamp=ipy.Timestamp.fromtimestamp(resp.mal_joined.timestamp()),
        )
        mal_embed.add_fields(
            *[
                ipy.EmbedField(
                    name="Username",
                    value=f"{resp.mal_username}"
                    if resp.mal_username not in [None, ""]
                    else "*Removed*",
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
            ]
        )
        mal_embed.set_thumbnail(
            url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
        )

        linked_platforms_embed = ipy.Embed(
            title="Linked Platforms Data",
            description="Below is your linked platforms data\nTo link a platform, use `/platform link`",
            color=0x9B1288,
            timestamp=ipy.Timestamp.fromtimestamp(resp.registered_at.timestamp()),
        )
        linked_platforms_embed.add_fields(
            *[
                ipy.EmbedField(
                    name="AniList",
                    value=f"{resp.anilist_username} (`{resp.anilist_id or 0}`)"
                    if resp.anilist_username not in [None, ""]
                    else "*Unset*",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Last.fm",
                    value=f"{resp.lastfm_username}"
                    if resp.lastfm_username not in [None, ""]
                    else "*Unset*",
                    inline=True,
                ),
                ipy.EmbedField(
                    name="Shikimori",
                    value=f"{resp.shikimori_username} (`{resp.shikimori_id}`)"
                    if resp.shikimori_username not in [None, ""]
                    else "*Unset*",
                    inline=True,
                ),
            ]
        )
        linked_platforms_embed.set_thumbnail(
            url="https://3.bp.blogspot.com/-qlSGpgl64rI/Wqih4jf-CuI/AAAAAAABK20/aoPMsqSqO_EEXE4d39WUqSc0nbwTGoV-wCLcBGAs/s0/mark_chain_kusari.png"
        )

        birthday, err = await generate_birthday_embed(ctx)

        embeds = [discord_embed, database_embed, mal_embed, linked_platforms_embed]
        if err == 0:
            embeds.append(birthday)

        await ctx.send(embeds=embeds)


def setup(bot: ipy.AutoShardedClient):
    """Load the extension"""
    WhoAmI(bot)
