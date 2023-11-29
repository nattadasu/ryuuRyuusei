from interactions import (AutoShardedClient, Buckets, Client, Cooldown,
                          Extension, SlashCommand, SlashContext)

from classes.nekomimidb import NekomimiGender
from modules.nekomimidb import submit_nekomimi


class Nekomimi(Extension):
    """NekomimiDB commands"""

    base = SlashCommand(
        name="nekomimi",
        description="Get a character in cat ears art",
        cooldown=Cooldown(
            cooldown_bucket=Buckets.USER,
            rate=1,
            interval=3,
        ),
    )
    group = base.group(name="random", description="Get random image")

    @group.subcommand(
        sub_cmd_name="boy",
        sub_cmd_description="Get a boy character in cat ears",
    )
    async def nekomimi_random_boy(self, ctx: SlashContext):
        await submit_nekomimi(ctx=ctx, gender=NekomimiGender.BOY)

    @group.subcommand(
        sub_cmd_name="girl",
        sub_cmd_description="Get a girl character in cat ears",
    )
    async def nekomimi_random_girl(self, ctx: SlashContext):
        await submit_nekomimi(ctx=ctx, gender=NekomimiGender.GIRL)

    @group.subcommand(
        sub_cmd_name="any",
        sub_cmd_description="Get a random image whatever the gender is",
    )
    async def nekomimi_random_any(self, ctx: SlashContext):
        await submit_nekomimi(ctx=ctx)


def setup(bot: Client | AutoShardedClient):
    Nekomimi(bot)
