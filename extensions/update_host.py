from os import getpid, kill
from subprocess import check_output as chout
from subprocess import run as sub_run

from interactions import (
    Activity,
    ActivityType,
    Client,
    Embed,
    Extension,
    IntervalTrigger,
    SlashContext,
    Status,
    Task,
)

from extensions.hostsettings import hostsettings_head
from modules.commons import save_traceback_to_file
from modules.const import GIT_COMMIT_HASH


class UpdateDaemon(Extension):
    """Daemon to update bot remotely or automatically"""

    def __init__(self, bot: Client) -> None:
        """Initialize the daemon"""
        self.bot = bot
        self.bot_client = bot.user
        self.GITHUB_COMMIT = GIT_COMMIT_HASH

    @staticmethod
    def _check_upstream_commit() -> str:
        """Check if there is any new commit in the upstream"""
        sub_run("git fetch", shell=True)
        upstream_commit = (
            chout(["git", "rev-parse", "origin"], shell=True).decode("utf-8").strip()
        )
        return upstream_commit

    def _pull_from_upstream(self) -> bool:
        """Pull the latest changes from the upstream"""
        try:
            sub_run("git pull", shell=True, check=True)
            return True
        except Exception as e:
            save_traceback_to_file(
                command="update_host",
                author=self.bot_client,
                error=e,
                mute_error=True,
            )
            return False

    @staticmethod
    def _update_pip_dependencies(is_dev: bool = False) -> bool:
        """Update the pip dependencies"""
        dev = "-dev" if is_dev else ""
        deps = chout(f"pip install -r requirements{dev}.txt", shell=True).decode(
            "utf-8"
        )
        # check if the dependencies are updated
        if "Successfully installed" in deps:
            return True
        return False

    async def _change_presence(self, context: str = "update") -> None:
        """Change presence to announce if the bot will do a reboot"""
        await self.bot.change_presence(
            activity=Activity(
                name=f"bot rebooting due to {context}",
                type=ActivityType.WATCHING,
            ),
            status=Status.IDLE,
        )

    async def _force_shutdown(self):
        """Force shutdown the bot"""
        await self._change_presence()
        pid = getpid()
        try:
            kill(pid, 9)
        except ProcessLookupError:
            save_traceback_to_file(
                command="update_host",
                author=self.bot_client,
                error=ProcessLookupError("No such process found"),
                mute_error=True,
            )
        except PermissionError:
            save_traceback_to_file(
                command="update_host",
                author=self.bot_client,
                error=PermissionError(
                    "Permission denied to kill the process; try running as root"
                ),
            )

    def _git_hash_not_matching(self) -> bool:
        """Check if the git hash is not matching"""
        upstream = None
        try:
            upstream = self._check_upstream_commit()
        except Exception:
            # Force to continue if the upstream is not reachable
            pass
        return self.GITHUB_COMMIT != upstream

    @Task.create(IntervalTrigger(days=7))
    async def check_for_updates(self) -> None:
        """Check for updates in the upstream"""
        upstream_commit = self._check_upstream_commit()
        if upstream_commit != self.GITHUB_COMMIT:
            self._update_pip_dependencies()
            await self._force_shutdown()

    @hostsettings_head.subcommand(
        sub_cmd_name="update",
        sub_cmd_description="Update the bot to the latest version",
    )
    async def update_host(self, ctx: SlashContext) -> None:
        """Update the bot to the latest version"""
        embed = Embed(
            title="Updating the bot",
            description="Please wait while the bot is being updated",
            color=0x4444FF,
        )
        msg = await ctx.send(embed=embed)
        if self._git_hash_not_matching():
            embed.add_field(
                name="🔀 Git", value="Pulling the latest changes from the upstream"
            )
            if self._pull_from_upstream():
                embed.add_field(name="🔧 Pip", value="Updating the pip dependencies")
                if self._update_pip_dependencies():
                    await msg.edit(embed=embed)
                else:
                    embed.add_field(
                        name="❌ Pip", value="Failed to update the pip dependencies"
                    )
                embed.add_field(
                    name="🔄 Restart", value="Restarting the bot to apply changes"
                )
                embed.title = "Update successful"
                embed.description = "The bot has been updated successfully"
                await msg.edit(embed=embed)
                await self._force_shutdown()
            else:
                embed.add_field(
                    name="❌ Git",
                    value="Failed to pull the latest changes from the upstream",
                )
        else:
            embed.add_field(
                name="🔀 Git",
                value=f"No new changes found in the upstream. Hash: `{GIT_COMMIT_HASH}`",
            )
            embed.title = "No updates found"
            embed.description = "The bot is already up-to-date"
        await msg.edit(embed=embed)

    @hostsettings_head.subcommand(
        sub_cmd_name="force_restart",
        sub_cmd_description="Force restart the bot",
    )
    async def force_restart(self, ctx: SlashContext) -> None:
        """Force restart the bot"""
        embed = Embed(
            title="Restarting the bot",
            description="Please wait while the bot is being restarted",
            color=0xFF4444,
        )
        await ctx.send(embed=embed)
        await self._force_shutdown()
