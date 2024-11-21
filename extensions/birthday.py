from asyncio import sleep
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Optional

import interactions as ipy
import numpy as np
import pandas as pd
import zoneinfo as zinf
from aiohttp import ClientSession
from fuzzywuzzy import fuzz  # type: ignore
from interactions.ext.paginators import Paginator

from classes.cache import Caching
from classes.database import UserBirthdayPermission, UserDatabase
from modules.commons import PlatformErrType, platform_exception_embed, save_traceback_to_file
from modules.const import BIRTHDAY_SERVER, BIRTHDAY_WEBHOOK

Cache = Caching("cache/birthday", 86400)


knowns = list(zinf.available_timezones())
knowns.sort()


@dataclass
class TimeZoneInfo:
    iana: str
    aka: str
    offset: str


def iana_to_dataclass(iana: str) -> TimeZoneInfo:
    tzinfo = zinf.ZoneInfo(iana)
    rn = datetime.now(tzinfo)
    return TimeZoneInfo(
        iana=iana,
        aka=rn.strftime("%Z"),
        offset=rn.strftime("%:z"),
    )


def iana_to_dict(iana: str) -> dict[str, str]:
    get = iana_to_dataclass(iana)
    return {
        "name": f"{get.iana} ({get.aka}, {get.offset})",
        "value": get.iana,
    }


def lookup_timezone(query: str) -> Iterable[dict[str, str]]:
    lookup_table: list[TimeZoneInfo] = []
    result: list[dict[str, str]] = []
    # use pandas to create a timezone lookup table
    for tz in knowns:
        lookup_table.append(iana_to_dataclass(tz))
    # create a dataframe
    df = pd.DataFrame(lookup_table)
    # fuzzy search
    for _, row in df.iterrows():  # type: ignore
        iana_score = fuzz.partial_ratio(query, row.iana)  # type: ignore
        aka_score = fuzz.partial_ratio(query, row.aka)  # type: ignore
        offset_score = fuzz.partial_ratio(query, row.offset)  # type: ignore
        score = max(iana_score, aka_score, offset_score)
        if score >= 70:
            result.append(
                {
                    "name": f"{row.iana} ({row.aka}, {row.offset})",
                    "value": row.iana,
                    "score": score,  # type: ignore
                }
            )
    # sort the result by score
    result.sort(key=lambda x: x["score"], reverse=True)
    for i, _ in enumerate(result):
        result[i].pop("score")
    return result[:25]


async def generate_birthday_embed(ctx: ipy.SlashContext) -> tuple[ipy.Embed, int]:
    async with UserDatabase() as udb:
        if not await udb.check_if_registered(ctx.author.id):
            pfembed = platform_exception_embed(
                description="You are not registered in the database! Please register first with `/register`",
                error="User not registered",
                error_type=PlatformErrType.USER,
            )
            return (pfembed, 1)
        usrdata = await udb.get_user_data(ctx.author.id)
        bday = usrdata.user_birthdate
        if bday is None:
            pfembed = platform_exception_embed(
                description="You have not set your birthday yet!",
                error="Birthday not set",
                error_type=PlatformErrType.USER,
            )
            return (pfembed, 1)
        tz = usrdata.user_timezone
    embed = ipy.Embed(
        title="Your birthday information",
        description="-# To unset your birthday, use `/birthday unset`",
    )
    embed.set_thumbnail("https://i.imgur.com/5wu9zcy.png")
    embed.add_field(
        name="Birthday",
        value=bday.strftime("%Y-%m-%d"),
        inline=True,
    )
    embed.add_field(
        name="Timezone",
        value=str(tz),
        inline=True,
    )
    perm = usrdata.birthday_permissions or UserBirthdayPermission(0)
    embed.add_field(
        name="Show year to others",
        value="Yes" if perm.show_year else "No",
        inline=True,
    )
    embed.add_field(
        name="Show age to others",
        value="Yes" if perm.show_age else "No",
        inline=True,
    )
    embed.add_field(
        name="Use Korean age system instead",
        value="Yes" if perm.use_korean_age else "No",
        inline=True,
    )
    return (embed, 0)


birthday_head = ipy.SlashCommand(
    name="birthday",
    description="Manage your birthday information",
    cooldown=ipy.Cooldown(
        cooldown_bucket=ipy.Buckets.USER,
        rate=1,
        interval=5,
    ),
    scopes=[BIRTHDAY_SERVER],
)

gifs = [
    "https://media1.tenor.com/m/nCZ3FCWmgC0AAAAd/happy-birthday-anime.gif",
    "https://media1.tenor.com/m/ESBGbKnIl_YAAAAd/happy-birthday.gif",
    "https://media1.tenor.com/m/OXva3hKNaVkAAAAd/birthday-cake.gif",
    "https://media1.tenor.com/m/wv2pZAuq4_AAAAAd/sanrio-boys-ryo-nishimiya.gif",
    "https://media1.tenor.com/m/Egxl8TRxwT4AAAAd/happy-birthday-anya.gif",
    "https://media1.tenor.com/m/VP1naZ8TZlQAAAAd/miku-cumple.gif",
    "https://media1.tenor.com/m/MvPvyKfXVCwAAAAd/lucky-star-anime.gif",
    "https://media1.tenor.com/m/0W0v33ReD7gAAAAd/happy-birthday-kitten.gif",
    "https://media1.tenor.com/m/BE8SYRkuz3kAAAAd/happy-birthday-anime-anime-birthday.gif",
    "https://media1.tenor.com/m/arXzNN9LCU4AAAAd/birthday-yippe.gif",
    "https://media1.tenor.com/m/QnL9JNK4A30AAAAd/fish-kiss.gif",
]

greets = [
    "happy birthday, since ur old enough you have to pay rent. Get a job",
    "happy birthday, you are now one year closer to death :wink:",
    "Wait, it's your birthday? I thought you were immortal",
    "So, you're telling me you were born on this day? I don't believe you",
    "Please don't tell me you're getting older, I don't want to feel old",
    "poof! happy birthday! now you're older and realize you're still broke",
    "quick! make a wish! I wish you get a job",
    "oops! I forgot to buy you a present, so here's a birthday greeting instead",
    "you're one year older, but you're still the same person, so that's good",
    "you're older now, surely you can buy yourself discord nitro",
    "happy birthday! now you're one year closer to getting a life",
    "another year older, another year wiser, another year to regret",
    'did you know? "happy birthday" is a song that is copyrighted',
    "congratulations! you've leveled up in life",
    "x years ago, you were born. now you're here. what a journey",
    "birthday? more like birth-yay!",
    "the cake is a lie, but the birthday greeting is real!!1!1!",
    "what's the best thing about birthdays? the cake, of course!",
    "wake up, it's your birthday! now go back to sleep",
    "remember, age is just a number. a really big number, but still a number... yes....",
    "UwU happy birthday, senpai! OwO",
    "kyaa~! happy birthday, onii-chan! uwu",
    "congrats! you've wasted another year of your life! now go waste another one!",
    "happy birthday! you're not just older; you're closer to the senior discount. yay savings!",
    "another year older? don’t worry, the wrinkles are just wisdom stretch marks",
    "congrats, you’ve survived another 365 days of adulting. barely, but hey, it counts!",
    "happy birthday! if you feel a draft, that's just the grim reaper breathing down your neck",
    'birthday candles are just tiny fire hazards screaming "you' 're ancient"',
    "they say with age comes wisdom. how’s that working out for you?",
    "happy birthday! at least you're not as old as you'll be next year",
    "if birthdays were achievements, yours would be 'seasoned pro at breathing'",
    "hey, it's your birthday! time to remind everyone that you're *still* single",
    "remember, every birthday is a chance to make questionable life choices. go nuts!",
    "happy birthday! today’s your day to eat cake and cry about your life choices",
    "don’t think of it as getting older. think of it as getting closer to free bus rides",
    "happy birthday! another year of people pretending they didn’t forget!",
    "happy birthday! another year of surviving my terrible jokes",
    "you're not getting older, you're just getting more distinguished. and wrinkled",
    "you know you're getting old when the candles cost more than the cake",
    "happy birthday! now spend your time wisely. by which I mean, waste it all on discord",
    "happy birthday! spend your day with your loved ones. or, you know, your waifu and husbando collections :3",
    "↓↓↑↑→←→←BABA SE—wait, wrong combo.... but do you know that this message doesnt have a meaning on it? right? now eat that cake",
]


class Birthday(ipy.Extension):
    """Extension for birthday-related commands, only runnable on private server"""

    def __init__(self, bot: ipy.Client | ipy.AutoShardedClient) -> None:
        """Initialize the extension"""
        self.bot: ipy.Client = bot
        self.birthday_announcer.start()

    @ipy.Task.create(ipy.CronTrigger("*/1 * * * *"))
    async def birthday_announcer(self) -> None:
        """Announce birthdays to the target channel"""
        async with UserDatabase() as udb:
            users = await udb.get_all_users()

        announced: list[int] = []
        now = datetime.now(tz=zinf.ZoneInfo("UTC"))
        yesterday = now.replace(day=now.day - 1)
        now = now.strftime("%Y-%m-%d")
        yesterday = yesterday.strftime("%Y-%m-%d")
        cache_path = Cache.get_cache_path(now)
        yesterday_cache = Cache.get_cache_path(yesterday)
        """Do not announce the same birthday twice"""
        cached: list[int] | None = Cache.read_cache(cache_path)
        yesterday_cached: list[int] | None = Cache.read_cache(yesterday_cache)
        if cached is not None:
            announced.extend(cached)
        if yesterday_cached is not None:
            announced.extend(yesterday_cached)
        for user in users:
            ubday = user.user_birthdate
            if ubday is None:
                continue
            if user.user_timezone is None:
                continue
            if int(user.discord_id) in announced:
                continue
            now = datetime.now(zinf.ZoneInfo(user.user_timezone))
            if not (ubday.day == now.day and ubday.month == now.month):
                continue
            age = now.year - ubday.year
            perm = user.birthday_permissions
            if perm is None:
                perm = UserBirthdayPermission(0)
            if perm.use_korean_age:
                age += 1
            usr = await self.bot.fetch_user(user.discord_id)
            usr_http = await self.bot.http.get_user(user.discord_id)
            http_data = None
            if usr:
                http_data = ipy.User.from_dict(usr_http, self.bot)  # type: ignore
            unnecessary_greet = np.random.choice(greets)
            msg_embed = ipy.Embed(
                title="Happy Birthday!",
                description=(
                    f"It's <@{user.discord_id}> birthday! 🎉\n\n"
                    f"> {unnecessary_greet}\n"
                    "-# Yes, it's AI (pre-)generated greeting ✨"
                ),
                # Randomize the color
                color=np.random.randint(0, 0xFFFFFF),
                timestamp=ipy.Timestamp.fromdatetime(datetime.now()),
            )
            if http_data and http_data.accent_color:
                msg_embed.color = http_data.accent_color.value
            if usr is not None and usr.avatar_url:
                msg_embed.set_thumbnail(url=usr.avatar_url)
            if perm.show_age:
                msg_embed.add_field(
                    name="Now turning", value=str(age) + " years old", inline=True
                )
            if perm.show_year:
                msg_embed.add_field(
                    name="Survived since:tm:", value=ubday.strftime("%Y"), inline=True
                )
            msg_embed.set_image("https://i.imgur.com/qHlVyJt.png")
            print(f"Announcing birthday for {user.discord_id}")
            gif = np.random.choice(gifs)
            msg_embed.set_image(gif)
            # cancel webhook if none
            if BIRTHDAY_WEBHOOK in ["", '""']:
                continue
            try:
                async with ClientSession() as session:
                    await session.post(
                        BIRTHDAY_WEBHOOK,
                        json={
                            "embeds": [msg_embed.to_dict()],
                            "content": f"<@{user.discord_id}>",
                            # use bot's avatar
                            "avatar_url": self.bot.user.avatar_url,
                            # use bot's username
                            "username": self.bot.user.username,
                        },
                    )
                await sleep(1)
            except Exception as ex:
                save_traceback_to_file("tasker_birthday", self.bot, ex)
            announced.append(int(user.discord_id))
        # Remove yesterday_cached entries from announced
        if yesterday_cached is not None:
            announced = [x for x in announced if x not in yesterday_cached]
        Cache.write_cache(cache_path, announced)

    @birthday_head.subcommand(
        sub_cmd_name="set",
        sub_cmd_description="Set your birthday",
        options=[
            ipy.SlashCommandOption(
                name="date",
                description="Your birthday, use YYYY-MM-DD format!",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="timezone",
                description="Your timezone, uses IANA timezone code (e.g. Asia/Jakarta, Etc/UTC, etc.)",
                type=ipy.OptionType.STRING,
                required=True,
                autocomplete=True,
            ),
            ipy.SlashCommandOption(
                name="show_year",
                description="Show the year of your birthdate publicly",
                type=ipy.OptionType.BOOLEAN,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="show_age",
                description="Show your age publicly",
                type=ipy.OptionType.BOOLEAN,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="korean_age",
                description="Use Korean age system instead",
                type=ipy.OptionType.BOOLEAN,
                required=False,
            ),
        ],
    )
    async def birthday_set(
        self,
        ctx: ipy.SlashContext,
        date: str,
        timezone: str,
        show_year: bool = True,
        show_age: bool = True,
        korean_age: bool = False,
    ):
        """Set your birthday"""
        await ctx.defer(ephemeral=True)
        if timezone == "Etc/None":
            await ctx.send(
                embed=ipy.Embed(
                    title="Timezone is not set",
                    description="Please set your timezone by selecting one of most used timezone, or type the timezone manually.\nYou can also use `Etc/UTC` if you don't know or want to hide your timezone",
                    color=0xFF0000,
                )
            )
            return
        try:
            _ = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await ctx.send(
                embed=ipy.Embed(
                    title="Invalid date format",
                    description="Please use YYYY-MM-DD format",
                    color=0xFF0000,
                )
            )
            return
        try:
            _ = zinf.ZoneInfo(timezone)
        except zinf.ZoneInfoNotFoundError:
            await ctx.send(
                embed=ipy.Embed(
                    title="Invalid timezone",
                    description="Please use IANA timezone format (e.g. Asia/Jakarta, Etc/UTC)",
                    color=0xFF0000,
                )
            )
            return
        async with UserDatabase() as udb:
            if not await udb.check_if_registered(ctx.author.id):
                pfembed = platform_exception_embed(
                    description="You are not registered in the database! Please register first with `/register`",
                    error="User not registered",
                    error_type=PlatformErrType.USER,
                )
                await ctx.send(embed=pfembed)
                return
            usrdata = await udb.get_user_data(ctx.author.id)
            bday = usrdata.user_birthdate
            if bday is not None:
                pfembed = platform_exception_embed(
                    description="You have already set your birthday! If you want to change it, unset your birthday by `/birthday unset`",
                    error="Birthday already set",
                    error_type=PlatformErrType.USER,
                )
                await ctx.send(embed=pfembed)
                return
            await udb.update_user(ctx.author.id, "userBirthdate", date)
            await udb.update_user(ctx.author.id, "userTimezone", timezone)
            await udb.update_user(
                ctx.author.id,
                "userBirthdayPermission",
                UserBirthdayPermission.from_dict(
                    {
                        "show_year": show_year,
                        "show_age": show_age,
                        "use_korean_age": korean_age,
                    }
                ).identifier,
            )
        await ctx.send(
            embed=ipy.Embed(
                title="Birthday set!",
                description=f"Your birthday has been set to {date} with timezone {timezone}",
                color=0x00FF00,
            )
        )

    @birthday_head.subcommand(
        sub_cmd_name="get",
        sub_cmd_description="Get your birthday",
    )
    async def birthday_get(self, ctx: ipy.SlashContext):
        """Get your birthday"""
        await ctx.defer(ephemeral=True)
        embed, _ = await generate_birthday_embed(ctx=ctx)
        await ctx.send(embed=embed)

    @birthday_head.subcommand(
        sub_cmd_name="edit",
        sub_cmd_description="Edit information about your birthday",
        options=[
            ipy.SlashCommandOption(
                name="date",
                description="Your birthday, use YYYY-MM-DD format!",
                type=ipy.OptionType.STRING,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="timezone",
                description="Your timezone, uses IANA timezone code (e.g. Asia/Jakarta, Etc/UTC, etc.)",
                type=ipy.OptionType.STRING,
                required=False,
                autocomplete=True,
            ),
            ipy.SlashCommandOption(
                name="show_year",
                description="Show the year of your birthdate publicly",
                type=ipy.OptionType.BOOLEAN,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="show_age",
                description="Show your age publicly",
                type=ipy.OptionType.BOOLEAN,
                required=False,
            ),
            ipy.SlashCommandOption(
                name="korean_age",
                description="Use Korean age system instead",
                type=ipy.OptionType.BOOLEAN,
                required=False,
            ),
        ],
    )
    async def birthday_edit(
        self,
        ctx: ipy.SlashContext,
        date: Optional[str] = None,
        timezone: Optional[str] = None,
        show_year: bool = False,
        show_age: bool = False,
        korean_age: bool = False,
    ):
        """Edit your birthday information"""
        await ctx.defer(ephemeral=True)
        configured: list[dict[str, str]] = []
        # if no options are provided, cancel the command
        if (
            date is None
            and timezone is None
            and not show_year
            and not show_age
            and not korean_age
        ):
            await ctx.send(
                embed=ipy.Embed(
                    title="No options provided",
                    description="Please provide at least one option to edit",
                    color=0xFF0000,
                )
            )
            return
        async with UserDatabase() as udb:
            user = await udb.get_user_data(ctx.author.id)
            if date:
                try:
                    _ = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    await ctx.send(
                        embed=ipy.Embed(
                            title="Invalid date format",
                            description="Please use YYYY-MM-DD format",
                            color=0xFF0000,
                        )
                    )
                    return
                await udb.update_user(ctx.author.id, "userBirthdate", date)
                configured.append(
                    {
                        "name": "Birthday",
                        "from": user.user_birthdate.strftime("%Y-%m-%d")
                        if user.user_birthdate
                        else "None",
                        "to": date,
                    }
                )
            if timezone:
                try:
                    _ = zinf.ZoneInfo(timezone)
                except zinf.ZoneInfoNotFoundError:
                    await ctx.send(
                        embed=ipy.Embed(
                            title="Invalid timezone",
                            description="Please use IANA timezone format (e.g. Asia/Jakarta, Etc/UTC)",
                            color=0xFF0000,
                        )
                    )
                    return
                await udb.update_user(ctx.author.id, "userTimezone", timezone)
                configured.append(
                    {
                        "name": "Timezone",
                        "from": user.user_timezone or "None",
                        "to": timezone,
                    }
                )
            perms = user.birthday_permissions
            if not perms:
                perms = UserBirthdayPermission(0)
            if show_year:
                perms.show_year = show_year
            if show_age:
                perms.show_age = show_age
            if korean_age:
                perms.use_korean_age = korean_age

            old = user.birthday_permissions
            if not old:
                old = UserBirthdayPermission(0)
            await udb.update_user(
                ctx.author.id, "userBirthdayPermission", perms.identifier
            )
            # Convert from dicts of permissions to one string
            # eg. New: k=Yes, s=No, y=Yes
            old_str = ", ".join(
                [f"{k}={'Yes' if v else 'No'}" for k, v in old.to_dict().items()]
            )
            new_str = ", ".join(
                [f"{k}={'Yes' if v else 'No'}" for k, v in perms.to_dict().items()]
            )
            if show_year or show_age or korean_age:
                configured.append(
                    {
                        "name": "Privacy settings",
                        "from": old_str,
                        "to": new_str,
                    }
                )
        field = "### Updated configuration:"
        for val in configured:
            field += f"\n* **{val['name']}**: {val['from']} → {val['to']}"
        await ctx.send(
            embed=ipy.Embed(
                title="Birthday information updated!",
                description=f"Your birthday information has been updated\n{field}",
                color=0x00FF00,
            )
        )

    @birthday_head.subcommand(
        sub_cmd_name="unset",
        sub_cmd_description="Unset your birthday",
    )
    async def birthday_unset(self, ctx: ipy.SlashContext):
        """Unset your birthday"""
        await ctx.defer()
        async with UserDatabase() as udb:
            if not await udb.check_if_registered(ctx.author.id):
                pfembed = platform_exception_embed(
                    description="You are not registered in the database! Please register first with `/register`",
                    error="User not registered",
                    error_type=PlatformErrType.USER,
                )
                await ctx.send(embed=pfembed)
                return
            usrdata = await udb.get_user_data(ctx.author.id)
            bday = usrdata.user_birthdate
            if bday is None:
                pfembed = platform_exception_embed(
                    description="You have not set your birthday yet!",
                    error="Birthday not set",
                    error_type=PlatformErrType.USER,
                )
                await ctx.send(embed=pfembed)
                return
            await udb.update_user(ctx.author.id, "userBirthdate", None)
            await udb.update_user(ctx.author.id, "userTimezone", None)
        await ctx.send(
            embed=ipy.Embed(
                title="Birthday unset!",
                description="Your birthday has been unset",
                color=0x00FF00,
            )
        )

    @birthday_head.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="List all birthdays",
    )
    async def birthday_list(self, ctx: ipy.SlashContext):
        """List all birthdays"""
        await ctx.defer()
        async with UserDatabase() as udb:
            users = await udb.get_all_users()
        result: dict[str, list[dict[str, str | int]]] = {}
        today = datetime.now()
        # automatically generate value-empty months
        for month in range(1, 13):
            result[datetime(2000, month, 1).strftime("%B")] = []
        for user in users:
            if user.user_birthdate is None:
                continue
            if user.user_timezone is None:
                continue
            month = user.user_birthdate.strftime("%B")
            age = (
                datetime.now(zinf.ZoneInfo(user.user_timezone)).year
                - user.user_birthdate.year
            )
            perm = user.birthday_permissions
            if perm is None:
                perm = UserBirthdayPermission(0)
            if perm.use_korean_age:
                age += 1
            result[month].append(
                {
                    "userid": str(user.discord_id),
                    # no leading zero
                    "birthdate": int(user.user_birthdate.strftime("%-d")),
                    "timezone": str(user.user_timezone),
                    "age": str(age) if perm.show_age else "??",
                }
            )
        # add today marker
        result[today.strftime("%B")].append(
            {
                "userid": "TODAY",
                "birthdate": today.day,
                "timezone": "Etc/UTC",
                "age": "??",
            }
        )
        embeds: list[ipy.Embed] = []
        irasutoya: dict[str, str] = {
            "January": "https://i.imgur.com/jOiBUHP.png",
            "February": "https://i.imgur.com/hYAElWW.png",
            "March": "https://i.imgur.com/Beh2QxW.png",
            "April": "https://i.imgur.com/98gtQ4L.png",
            "May": "https://i.imgur.com/MIju0TQ.png",
            "June": "https://i.imgur.com/puULheQ.png",
            "July": "https://i.imgur.com/V0lSMgM.png",
            "August": "https://i.imgur.com/XCQ2sDr.png",
            "September": "https://i.imgur.com/r3Nfh42.png",
            "October": "https://i.imgur.com/r7DOqGh.png",
            "November": "https://i.imgur.com/1Gsg4D1.png",
            "December": "https://i.imgur.com/JHFHBFT.png",
        }
        for month, data in result.items():
            if not data:
                continue
            embed = ipy.Embed(
                title=f"Birthdays in {month}",
                description=f"Here are the list of birthdays in {month}",
            )
            # reserve fields by 7 days, 4 fields in total
            fields: list[ipy.EmbedField] = []
            for i in range(0, 31, 7):
                listed: list[str] = []
                for user in data:
                    usr_month = datetime.strptime(
                        f"{user['birthdate']} {month} {today.year}", "%d %B %Y"
                    )
                    if user["userid"] == "TODAY" and i < today.day <= i + 7:
                        context = f"* {today.strftime('%d')}: **\\>\\>\\> TODAY \\<\\<\\<**"
                        listed.append(context)
                        continue
                    if i < int(user["birthdate"]) <= i + 7:
                        context = f"* {user['birthdate']}: <@{user['userid']}>"
                        age = user["age"]
                        if user["age"] == "??":
                            listed.append(context)
                            continue
                        context += f" (age {age}"
                        if today.month > usr_month.month:
                            context += f", next year {int(age)+1})"
                        else:
                            context += ")"
                        listed.append(context)
                if not listed:
                    continue
                # sort the listed
                listed.sort()
                final = "\n".join(listed)
                day_from = i + 1
                day_limit = i + 7
                # use last day of the month if the day limit exceeds
                mnend = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
                if day_limit > mnend.day:
                    day_limit = mnend.day
                index = f"{day_from} to {day_limit}" if day_from < day_limit else f"{day_from}"
                fields.append(
                    ipy.EmbedField(
                        name=f"Day {index}",
                        value=final,
                        inline=True,
                    )
                )
            embed.add_fields(*fields)
            embed.set_image(url=irasutoya[month])
            embed.set_footer(
                text="Clipart by いらすとや // Add your birthday with `/birthday set`"
            )
            embeds.append(embed)
        paginator = Paginator.create_from_embeds(self.bot, *embeds, timeout=60)
        await paginator.send(ctx)

    @birthday_set.autocomplete("timezone")
    @birthday_edit.autocomplete("timezone")
    async def timezone_autocomplete(self, ctx: ipy.AutocompleteContext):
        if ctx.input_text in ["", None, " "]:
            reccs = [
                "Etc/UTC",
                "America/New_York",
                "Asia/Jakarta",
                "Asia/Kolkata",
                "Asia/Tokyo",
                "Australia/Sydney",
                "Europe/London",
            ]
            choices: list[dict[str, str]] = [
                {
                    "name": "Start typing to search, or pick from the list below",
                    "value": "Etc/None",
                }
            ]
            final: list[dict[str, str]] = []
            for r in reccs:
                final.append(iana_to_dict(r))
            # combine reccs with choices
            choices.extend(final)
            await ctx.send(choices=choices)
            return
        # Generate timezone list
        await ctx.send(choices=lookup_timezone(ctx.input_text))


def setup(bot: ipy.Client | ipy.AutoShardedClient) -> None:
    Birthday(bot)
