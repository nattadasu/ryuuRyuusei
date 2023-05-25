"""
# MyAnimeList Module

This module contains modules that are related to MyAnimeList or Jikan API.
"""

import html
import re
from datetime import datetime, timezone
from enum import Enum
from urllib.parse import quote
from zoneinfo import ZoneInfo

import pandas as pd
from interactions import (
    Button,
    ButtonStyle,
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedFooter,
    SlashContext,
)

from classes.anilist import AniList, AniListImageStruct, AniListMediaStruct
from classes.animeapi import AnimeApi, AnimeApiAnime
from classes.jikan import JikanApi
from classes.kitsu import Kitsu
from classes.myanimelist import MyAnimeList
from classes.simkl import Simkl
from modules.commons import (
    generate_commons_except_embed,
    generate_trailer,
    get_parent_nsfw_status,
    get_random_seed,
    sanitize_markdown,
    trim_cyno,
)
from modules.const import (
    EMOJI_FORBIDDEN,
    EMOJI_UNEXPECTED_ERROR,
    EMOJI_USER_ERROR,
    MYANIMELIST_CLIENT_ID,
    SIMKL_CLIENT_ID,
    warnThreadCW,
)


def lookupRandomAnime() -> int:
    """
    Lookup random anime from MAL

    Args:
        None

    Returns:
        int: MAL ID of a random anime
    """
    seed = get_random_seed()
    # open database/mal.csv
    df = pd.read_csv("database/mal.csv", sep="\t")
    # get random anime
    randomAnime = df.sample(n=1, random_state=seed)
    # get anime id
    randomAnimeId: int = randomAnime["mal_id"].values[0]
    return randomAnimeId


async def searchMalAnime(title: str) -> dict | list:
    """
    Search anime via MyAnimeList API

    Args:
        title (str): Anime title

    Returns:
        dict | list: Anime data
    """
    fields = [
        "id",
        "title",
        "alternative_titles\\{ja\\}",
        "start_season",
        "media_type",
    ]
    fields = ",".join(fields)
    async with MyAnimeList(MYANIMELIST_CLIENT_ID) as mal:
        data = await mal.search(title, limit=5, fields=fields)
    for d in data["data"]:
        # drop main_picture
        d["node"].pop("main_picture", None)
        # only keep english and japanese alternative titles
        d["node"]["alternative_titles"] = {
            k: v
            for k, v in d["node"]["alternative_titles"].items()
            if k in ["en", "ja"]
        }
        # if d['node']['start_season'] is not in the dict, then force add as
        # None:
        if "start_season" not in d["node"]:
            d["node"]["start_season"] = {"year": None, "season": None}
        if "media_type" not in d["node"]:
            d["node"]["media_type"] = "unknown"
    return data["data"]


class MalErrType(Enum):
    """MyAnimeList Error Type"""

    USER = EMOJI_USER_ERROR
    NSFW = EMOJI_FORBIDDEN
    SYSTEM = EMOJI_UNEXPECTED_ERROR


def mal_exception_embed(
    description: str,
    error: str,
    lang_dict: dict,
    error_type: MalErrType | str = MalErrType.SYSTEM,
    color: hex = 0xFF0000,
) -> Embed:
    """
    Generate an embed for MyAnimeList exceptions

    Args:
        description (str): Description of the error
        error (str): Error message
        lang_dict (dict): Language dictionary
        error_type (MalErrType | str, optional): Error type. Defaults to MalErrType.SYSTEM.
        color (hex, optional): Embed color. Defaults to 0xFF0000.

    Returns:
        Embed: Embed object
    """
    l_ = lang_dict
    if isinstance(error_type, MalErrType):
        error_type = error_type.value
    else:
        error_type = str(error_type)
    emoji = re.sub(r"(<:.*:)(\d+)(>)", r"\2", error_type)
    dcEm = Embed(
        color=color,
        title=l_["commons"]["error"],
        description=description,
        fields=[EmbedField(name=l_["commons"]["reason"], value=error, inline=False)],
    )
    dcEm.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji}.png?v=1")

    return dcEm


class MediaIsNsfw(Exception):
    """Media is NSFW exception"""


# old code taken from ipy/v4.3.4
async def generate_mal(
    entry_id: int,
    is_nsfw: bool = False,
    al_dict: AniListMediaStruct | None = None,
    anime_api: AnimeApiAnime | None = None,
) -> list[Embed, Button]:
    """
    Generate an embed for /anime with MAL via Jikan

    Args:
        entry_id (int): MAL ID
        is_nsfw (bool, optional): NSFW status. Defaults to False.
        al_dict (AniListMediaStruct, optional): AniList data. Defaults to None.
        anime_api (dict, optional): Anime API data. Defaults to None.

    Raises:
        MediaIsNsfw: NSFW is not allowed

    Returns:
        list[Embed, Button]: Embed and button
    """

    async with JikanApi() as jikan:
        j = await jikan.get_anime_data(entry_id)

    al = al_dict

    msg_for_thread = warnThreadCW if is_nsfw is not None else ""

    if not is_nsfw:
        for g in j.genres:
            gn = g.name
            if "Hentai" in gn:
                raise MediaIsNsfw(
                    f"{EMOJI_FORBIDDEN} **NSFW is not allowed!**\nOnly NSFW channels are allowed to search NSFW content.{msg_for_thread}"
                )

    m = j.mal_id
    cyno = "*None*"

    if j.synopsis is not None:
        jdata = j.synopsis.replace("\n\n[Written by MAL Rewrite]", "")
        jdata = html.unescape(jdata)
        j_spl = jdata.split("\n")
        synl = len(j_spl)
        cynoin = j_spl[0]
        cynmo = (
            f"\n> \n> Read more on [MyAnimeList](<https://myanimelist.net/anime/{m}>)"
        )

        if len(str(cynoin)) <= 150:
            cyno = sanitize_markdown(cynoin)
            if synl >= 3:
                cyno += "\n> \n> "
                cyno += trim_cyno(sanitize_markdown(j_spl[2]))
        elif len(str(cynoin)) >= 1000:
            cyno = trim_cyno(sanitize_markdown(cynoin))
        else:
            cyno = sanitize_markdown(cynoin)

        if (
            (cyno[-3:] == "...")
            or ((len(str(cynoin)) >= 150) and (synl > 3))
            or ((len(str(cynoin)) >= 1000) and (synl > 1))
        ):
            cyno += cynmo

    jJpg = j.images.jpg
    note = "Images from "

    if not al:

        class al:
            coverImage = AniListImageStruct(extraLarge=None, large=None, color=None)
            bannerImage = None

    alPost = al.coverImage.extraLarge
    alBg = al.bannerImage

    try:
        async with Simkl(SIMKL_CLIENT_ID) as sim:
            smId = await sim.search_by_id(sim.Provider.MYANIMELIST, m)
            smk = await sim.get_anime(smId[0]["ids"]["simkl"])
    except Exception:
        smk = {"poster": None, "fanart": None}

    smkPost = smk.get("poster")
    smkBg = smk.get("fanart")
    smkPost = f"https://simkl.in/posters/{smkPost}_m.webp" if smkPost else None
    smkBg = f"https://simkl.in/fanart/{smkBg}_w.webp" if smkBg else None

    if anime_api.kitsu and ((not alPost and not alBg) or (not smkPost and not smkBg)):
        async with Kitsu() as kts:
            kts = await kts.get_anime(anime_api.kitsu)
    else:
        kts = {"data": {"attributes": {"posterImage": None, "coverImage": None}}}

    ktsPost = kts["data"]["attributes"].get("posterImage")
    ktsPost = ktsPost.get("original") if ktsPost else None
    ktsBg = kts["data"]["attributes"].get("coverImage")
    ktsBg = ktsBg.get("original") if ktsBg else None

    malPost = jJpg.large_image_url or jJpg.image_url
    malBg = ""

    poster = next((img for img in (alPost, smkPost, ktsPost, malPost) if img), None)
    postNote = (
        "AniList"
        if alPost
        else "SIMKL"
        if smkPost
        else "Kitsu"
        if ktsPost
        else "MyAnimeList"
    )
    background = next((img for img in (alBg, smkBg, ktsBg, malBg) if img), None)
    bgNote = (
        "AniList" if alBg else "SIMKL" if smkBg else "Kitsu" if ktsBg else "MyAnimeList"
    )

    if postNote == bgNote:
        note += f"{postNote} for poster and background."
    else:
        note += f"{postNote} for poster"
        if bgNote != "MyAnimeList":
            note += f" and {bgNote} for background."
        else:
            note += "."

    # Build sendMessages
    tgs = []
    tgs.extend(g.name for g in j.genres)
    tgs.extend(g.name for g in j.themes)
    tgs.extend(g.name for g in j.demographics)
    tgs.extend(f"||{g.name}||" for g in j.explicit_genres)

    ssonn = j.season
    daten = datetime(1970, 1, 1, tzinfo=timezone.utc)
    tgs = sorted(set(tgs), key=str.casefold)
    tgs = ", ".join(tgs) if tgs else "*None*"

    astn, aenn = j.aired.from_, j.aired.to
    year = str(astn.year) if astn else "year?"
    astr = j.aired.string
    bcast = j.broadcast

    # Grab studio names on j['studios'][n]['name']
    studio_names = [s.name for s in j.studios] if j.studios else None
    stdio = ", ".join(studio_names) if studio_names else "*None*"

    # start date logic
    if astn:
        if re.match(r"^([\d]{4})|^([a-zA-Z]{3} [\d]{4})", astr):
            ast = astr.split(" to ")[0]
            tsa = ""
        elif re.match(r"^([a-zA-Z]{3} [\d]{1,2}, [\d]{4})", astr):
            if bcast.string in ["Unknown", None] or bcast.time is None:
                ast = (astn - daten).total_seconds()
            else:
                # Split bcast.time into hours and minutes
                bct = bcast.time.split(":")
                prop = j.aired.from_
                # Convert bct to datetime
                ast = (
                    prop.replace(
                        hour=int(bct[0]),
                        minute=int(bct[1]),
                        tzinfo=ZoneInfo(bcast.timezone),
                    )
                    - daten
                ).total_seconds()
            ast = int(ast)
            tsa = f"(<t:{ast}:R>)"
            ast = f"<t:{ast}:D>"
    else:
        ast, tsa = "TBA", ""

    # end date logic
    # Check airing dates
    if aenn is not None:
        if re.match(r"^([a-zA-Z]{3} [\d]{1,2}, [\d]{4})", astr):
            if (bcast.string in ["Unknown", None]) or bcast.time is None:
                # Calculate time delta
                aen = (aenn - daten).total_seconds()
            else:
                # Split bcast.time into hours and minutes
                bct = bcast.time.split(":")
                prop = j.aired.to
                # Convert bct to datetime
                aen = (
                    prop.replace(
                        hour=int(bct[0]),
                        minute=int(bct[1]),
                        tzinfo=ZoneInfo(bcast.timezone),
                    )
                    - daten
                ).total_seconds()
            aen = str(int(aen)).removesuffix(".0")
            aen = f"<t:{aen}:D>"
        elif re.match(r"^([a-zA-Z]{3} [\d]{4})", astr):
            aen = astr.split(" to ")[1]
    else:
        if j.status == "Currently Airing":
            aen = "Ongoing"
        elif j.status == "Not yet aired" or astr == "Not available":
            aen = "TBA"
        else:
            aen = ast

    # Build date
    tsa = f" {tsa}" if tsa is not None else ""
    if ast == "TBA" and aen == "TBA":
        date = "TBA"
    else:
        date = f"{ast} - {aen}{tsa}"

    # Set season
    if ssonn is not None:
        sson = str(ssonn).capitalize()
    elif re.match("^[0-9]{4}$", ast):
        sson = "Unknown"
    elif j.aired.prop.from_.month is not None:
        sson = astn.strftime("%m")
        if sson in ["01", "02", "03"]:
            sson = "Winter"
        elif sson in ["04", "05", "06"]:
            sson = "Spring"
        elif sson in ["07", "08", "09"]:
            sson = "Summer"
        elif sson in ["10", "11", "12"]:
            sson = "Fall"
    else:
        sson = "Unknown"

        # Get title information
    rot = j.title
    nat = j.title_japanese or "*None*"
    ent = j.title_english

    # Create a synonyms list
    syns = [s.title for s in j.titles if s.type not in ["Default", "English"]]
    if not ent:
        # Set ent to a synonym in ASCII or the original title
        for s in syns:
            if re.match(r"([0-9a-zA-Z][:0-9a-zA-Z ]+)(?= )", s):
                ent = s
                break
        else:
            ent = rot

    if (ent is None) or (ent == ""):
        # for each s in syns, check if the s is in ASCII using regex
        # if it is, then set ent to s
        # if not, then set ent to rot
        for s in syns:
            if re.match(r"([0-9a-zA-Z][:0-9a-zA-Z ]+)(?= )", s):
                # grab group 1
                ent = s
                break
        else:
            ent = rot
        enChkMark = "\\*"
        chkMsg = "\n* Data might be inaccurate due to bot rules/config, please check source for more information."
    else:
        enChkMark = ""
        chkMsg = ""

    # Format synonyms list
    ogt = [rot, nat, ent]
    syns = sorted(set(syns) - set(ogt), key=str.casefold)
    synsl = len(syns)
    if synsl > 8:
        syns = ", ".join(syns[:8]) + f", *and {synsl - 8} more*"
    elif synsl > 1:
        syns = ", ".join(syns)
    elif synsl == 1:
        syns = syns[0]
    else:
        syns = "*None*"

    # Format number of votes
    pvd = j.scored_by if j.scored_by else 0
    pvd = (
        f"{pvd:,} people voted"
        if pvd > 1
        else "1 person voted"
        if pvd == 1
        else "0 person voted"
    )

    # Format number of episodes
    eps = j.episodes if j.episodes else "*Unknown*"

    # Format status
    stat = j.status if j.status else "*Unknown*"

    # Format duration
    dur = j.duration if j.duration else "*Unknown*"

    # Format score
    scr = j.score if j.score else "0"

    # Add check message to note
    note += chkMsg

    if str(eps) in ["1", "0", None]:
        episodeField = EmbedField(name="Duration", value=f"{dur}", inline=True)
    else:
        episodeField = EmbedField(
            name="Eps/Duration", value=f"{eps} ({dur})", inline=True
        )

    embed = Embed(
        author=EmbedAuthor(
            name="MyAnimeList Anime",
            url="https://myanimelist.net",
            icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png",
        ),
        title=rot,
        url=f"https://myanimelist.net/anime/{m}",
        description=f"""*`{m}`, {j.type}, {sson} {year}, ⭐ {scr}/10 by {pvd}*

> {cyno}
""",
        color=0x2E51A2,
        fields=[
            EmbedField(name=f"English Title{enChkMark}", value=ent, inline=True),
            EmbedField(name="Native Title", value=nat, inline=True),
            EmbedField(name="Synonyms", value=syns),
            EmbedField(name="Genres and Themes", value=tgs),
            episodeField,
            EmbedField(name="Status", value=stat, inline=True),
            EmbedField(name="Studio", value=stdio, inline=True),
            EmbedField(name="Aired", value=date),
        ],
        footer=EmbedFooter(text=note),
    )
    embed.set_thumbnail(url=poster)
    embed.set_image(url=background)
    anime_stats: Button = Button(
        style=ButtonStyle.URL,
        label="Anime Stats",
        url=f"https://anime-stats.net/anime/show/{quote(rot)}",
    )

    return [embed, anime_stats]


async def malSubmit(ctx: SlashContext, ani_id: int) -> None:
    """
    Send anime information from MAL to the channel

    Args:
        ctx (SlashContext): The context of the command
        ani_id (int): The anime ID

    Raises:
        *None*
    """
    await ctx.defer()
    channel = ctx.channel

    if channel.type in (11, 12):
        nsfwBool = await get_parent_nsfw_status(channel.parent_id)
    else:
        nsfwBool = channel.nsfw

    trailer = []
    try:
        async with AnimeApi() as aniapi:
            aniApi = await aniapi.get_relation(
                media_id=ani_id, platform=aniapi.AnimeApiPlatforms.MYANIMELIST
            )

        if aniApi.anilist is not None:
            async with AniList() as al:
                alData = await al.anime(media_id=aniApi.anilist)

                if alData.trailer and alData.trailer.site == "youtube":
                    trailer.append(generate_trailer(data=alData))
        else:
            alData = {}

        dcEm = await generate_mal(
            ani_id, is_nsfw=nsfwBool, al_dict=alData, anime_api=aniApi
        )
        trailer += [dcEm[1]]
        dcEm = dcEm[0]
        await ctx.send("", embeds=dcEm, components=trailer)

    except MediaIsNsfw as e:
        await ctx.send(f"**{e}**\n")

    except Exception as e:
        embed = generate_commons_except_embed(
            description="We are unable to get the anime information from MyAnimeList via Jikan",
            error=e,
        )
        await ctx.send("", embed=embed)
