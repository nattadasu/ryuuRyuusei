"""
This extension provides a help command that lists all available commands.

Portion of the code were taken from https://github.com/B1ue-Dev/Articuno
under the GPL-3.0 License, and heavily optimized using AI.

Notable changes:
* Sorting commands by name
* Fix paginator not showing all commands
  Original code uses `if i == 10`, which may orphans the last commands
  that isn't a multiple of 10
* Better readability of the code
* Removed unassigned variables
"""

import interactions as ipy
from interactions.ext.paginators import Paginator


class Help(ipy.Extension):
    """Help command"""

    @ipy.slash_command(name="help", description="Get a list of all available commands")
    async def help(self, ctx: ipy.SlashContext) -> None:
        """Get a list of all available commands."""
        help_list = []
        commands = sorted(self.bot.application_commands, key=lambda x: str(x.name))

        commands = [
            command
            for command in commands
            if command.scopes in ([0], [ctx.author.id], [ctx.guild.id])
        ]

        for i in range(0, len(commands), 10):
            listed = []
            for command in commands[i : i + 10]:
                if type(command) is not ipy.SlashCommand:
                    continue
                cmd_name = f"/{command.name}"
                group_name = f" {command.group_name}" if command.group_name else ""
                sub_cmd_name = (
                    f" {command.sub_cmd_name}" if command.sub_cmd_name else ""
                )
                name = f"{cmd_name}{group_name}{sub_cmd_name}"
                description = (
                    command.sub_cmd_description
                    if command.sub_cmd_name
                    else command.description
                )
                listed.append(ipy.EmbedField(name=f"{name}", value=f"{description}"))

            help_list.append(
                ipy.Embed(
                    title="List of available commands.",
                    color=0x7CB7D3,
                    thumbnail=ipy.EmbedAttachment(url=self.bot.user.avatar.url),
                    fields=listed,
                )
            )

        paginator = Paginator.create_from_embeds(self.bot, *help_list, timeout=30)
        await paginator.send(ctx)


def setup(bot: ipy.AutoShardedClient) -> None:
    """Load the extension."""
    Help(bot)
