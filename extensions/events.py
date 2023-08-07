import re
from time import time

import interactions as ipy
from interactions.api.events import CommandError, MemberAdd, MemberRemove, GuildJoin, GuildLeft

from modules.const import BOT_DATA, EMOJI_FORBIDDEN


class BotEvents(ipy.Extension):
    """Bot events"""

    async def update_presence(self) -> None:
        """Update bot presence"""
        server_members: dict[str, int] = BOT_DATA["server_members"]
        member_count = sum(server_members.values())
        final = f"{len(self.bot.guilds)} guilds, {member_count} members"
        await self.bot.change_presence(
            activity=ipy.Activity(
                name=final,
                type=ipy.ActivityType.WATCHING,
            ),
        )

    # increment BOT_DATA["member_count"] when a member joins
    @ipy.listen()
    async def on_member_add(self, event: MemberAdd):
        """When a member joins"""
        BOT_DATA["server_members"][f"{event.guild.id}"] += 1
        await self.update_presence()

    # decrement BOT_DATA["member_count"] when a member leaves
    @ipy.listen()
    async def on_member_remove(self, event: MemberRemove):
        """When a member leaves"""
        BOT_DATA["server_members"][f"{event.guild.id}"] -= 1
        await self.update_presence()

    @ipy.listen()
    async def on_guild_join(self, event: GuildJoin):
        """When the bot joins a guild"""
        BOT_DATA["server_members"][f"{event.guild.id}"] = event.guild.member_count
        await self.update_presence()

    @ipy.listen()
    async def on_guild_leave(self, event: GuildLeft):
        """When the bot leaves a guild"""
        del BOT_DATA["server_members"][f"{event.guild.id}"]
        await self.update_presence()

    @ipy.listen(disable_default_listeners=True)
    async def on_command_error(self, event: CommandError):
        """Handle command errors"""
        if isinstance(event.error, ipy.errors.CommandOnCooldown):
            emoji_id = re.search(r"<a?:\w+:(\d+)>", EMOJI_FORBIDDEN)
            emoji_id = emoji_id.group(1) if emoji_id else None
            now = time()
            remaining = now + event.error.cooldown.get_cooldown_time()
            embed = ipy.Embed(
                author=ipy.EmbedAuthor(
                    name="Forbidden action",
                ),
                title="You are on cooldown",
                description=f"Try again <t:{int(remaining)}:R>",
                color=0xFF0000,
            )
            if emoji_id:
                embed.set_thumbnail(
                    url=f"https://cdn.discordapp.com/emojis/{emoji_id}.webp"
                )
            await event.ctx.send(embed=embed, ephemeral=True)  # type: ignore
        else:
            await self.bot.on_command_error(self.bot, event)

    @ipy.component_callback("message_delete")
    async def message_delete(self, ctx: ipy.ComponentContext):
        """
        Delete the message that the button is in

        Args:
            ctx (ipy.ComponentContext): The context
        """
        if ctx.message is None:
            return
        # ref
        if ctx.message.interaction is None:
            return
        reference = ctx.message.interaction.user.id
        # check if the user is the author
        if ctx.author.id != reference:
            await ctx.send(
                f"{EMOJI_FORBIDDEN} You can not delete a command that you did not send, allowed for <@!{reference}>",
                ephemeral=True,
            )
            return
        await ctx.message.delete()


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    BotEvents(bot)
