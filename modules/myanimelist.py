"""
# MyAnimeList Module

This module contains modules that are related to MyAnimeList or Jikan API.
"""

import html
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

import pandas as pd
from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    ComponentContext,
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedFooter,
    Message,
    PartialEmoji,
    SlashContext,
)

from classes.anilist import AniList, AniListMediaStruct
from classes.animeapi import AnimeApi, AnimeApiAnime
from classes.excepts import MediaIsNsfw, ProviderHttpError
from classes.jikan import JikanApi
from classes.kitsu import Kitsu
from classes.myanimelist import MyAnimeList
from modules.commons import (
    PlatformErrType,
    generate_commons_except_embed,
    generate_trailer,
    get_nsfw_status,
    get_random_seed,
    platform_exception_embed,
    sanitize_markdown,
    save_traceback_to_file,
    send_or_edit_message,
    trim_synopsis,
)
from modules.const import MESSAGE_WARN_CONTENTS, MYANIMELIST_CLIENT_ID
from modules.platforms import Platform, media_id_to_platform


def generate_animethemes_slug(title: str) -> str:
    """
    Generate a slug for animethemes.moe with underscore

    Args:
        title (str): Anime title, must based from MyAnimeList

    Returns:
        str: slug for the title
    """

    # Remove any characters outside [\w\- ]+ in Regex
    title = re.sub(r"[^\w\- ]+", "", title)
    # Replace all whitespace and dash with underscore
    title = re.sub(r"[\s-]+", "_", title)
    # Remove duplicate underscore
    title = re.sub(r"__+", "_", title)
    # Remove any underscore at the beginning and end of the string
    title = re.sub(r"^_+|_+$", "", title)
    # Convert to lowercase
    title = title.lower()
    return title


def lookup_random_anime() -> int:
    """
    Lookup random anime from MAL

    Args:
        None

    Returns:
        int: MAL ID of a random anime
    """
    seed = get_random_seed()
    # open database/mal.csv
    dataframe = pd.read_csv("database/mal.csv", sep="\t")
    # get random anime
    rand_anime = dataframe.sample(n=1, random_state=seed)
    # get anime id
    rand_anime_id: int = rand_anime["mal_id"].values[0]
    return rand_anime_id


async def search_mal_anime(title: str) -> list[dict[str, Any]]:
    """
    Search anime via MyAnimeList API

    Args:
        title (str): Anime title

    Returns:
        list[dict[str, Any]]: Anime data
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
    for dat in data["data"]:
        # drop main_picture
        dat["node"].pop("main_picture", None)
        # only keep english and japanese alternative titles
        dat["node"]["alternative_titles"] = {
            k: v
            for k, v in dat["node"]["alternative_titles"].items()
            if k in ["en", "ja"]
        }
        # if d['node']['start_season'] is not in the dict, then force add as
        # None:
        if "start_season" not in dat["node"]:
            dat["node"]["start_season"] = {"year": None, "season": None}
        if "media_type" not in dat["node"]:
            dat["node"]["media_type"] = "unknown"
    return data["data"]


# old code taken from ipy/v4.3.4
async def generate_mal(
    entry_id: int,
    is_nsfw: bool | None = False,
    anilist_data: AniListMediaStruct | None = None,
    anime_api: AnimeApiAnime | None = None,
) -> tuple[Embed, list[Button]]:
    """
    Generate an embed for /anime with MAL via Jikan

    Args:
        entry_id (int): MAL ID
        is_nsfw (bool, optional): NSFW status. Defaults to False.
        anilist_data (AniListMediaStruct, optional): AniList data. Defaults to None.
        anime_api (dict, optional): Anime API data. Defaults to None.

    Raises:
        MediaIsNsfw: NSFW is not allowed

    Returns:
        list[Embed | list[ActionRow]]: Embed and button
    """

    async with JikanApi() as jikan:
        jk_dat = await jikan.get_anime_data(entry_id)

    if anilist_data is not None:
        alist: AniListMediaStruct = anilist_data
    else:
        alist: AniListMediaStruct = AniListMediaStruct(id=0)

    msg_for_thread = MESSAGE_WARN_CONTENTS if is_nsfw is not None else ""

    if not is_nsfw and jk_dat.genres is not None:
        for genre in jk_dat.genres:
            genre_name = genre.name
            if "Hentai" in genre_name:
                raise MediaIsNsfw(
                    f"Only NSFW channels are allowed to search NSFW content.{msg_for_thread}"
                )

    mal_id = jk_dat.mal_id
    cyno = "*None*"

    if jk_dat.synopsis is not None:
        jdata = jk_dat.synopsis.replace("\n\n[Written by MAL Rewrite]", "")
        jdata = html.unescape(jdata)
        j_spl = jdata.split("\n")
        synl = len(j_spl)
        cynoin = j_spl[0]
        cynmo = f"\n> \n> Read more on [MyAnimeList](<https://myanimelist.net/anime/{mal_id}>)"

        if len(str(cynoin)) <= 150:
            cyno = sanitize_markdown(cynoin)
            if synl >= 3:
                cyno += "\n> \n> "
                cyno += trim_synopsis(sanitize_markdown(j_spl[2]))
        elif len(str(cynoin)) >= 1000:
            cyno = trim_synopsis(sanitize_markdown(cynoin))
        else:
            cyno = sanitize_markdown(cynoin)

        if (
            (cyno[-3:] == "...")
            or ((len(str(cynoin)) >= 150) and (synl > 3))
            or ((len(str(cynoin)) >= 1000) and (synl > 1))
        ):
            cyno += cynmo

    if jk_dat.images is not None and jk_dat.images.jpg is not None:
        jjpg = jk_dat.images.jpg
    note = "Images from "

    al_post = None
    if alist.coverImage is not None:
        al_post = alist.coverImage.extraLarge
    al_bg = alist.bannerImage

    if anime_api is not None and anime_api.kitsu and (not al_post and not al_bg):
        async with Kitsu() as kts:
            kts = await kts.get_anime(anime_api.kitsu)
    else:
        kts = {"data": {"attributes": {"posterImage": None, "coverImage": None}}}

    kts_post = kts["data"]["attributes"].get("posterImage")
    kts_post: str | None = kts_post.get("original") if kts_post else None
    kts_bg = kts["data"]["attributes"].get("coverImage")
    kts_bg: str | None = kts_bg.get("original") if kts_bg else None

    mal_post = jjpg.large_image_url or jjpg.image_url
    mal_bg = ""

    poster = next((img for img in (al_post, kts_post, mal_post) if img), None)
    post_note = "AniList" if al_post else "Kitsu" if kts_post else "MyAnimeList"
    background = next((img for img in (al_bg, kts_bg, mal_bg) if img), None)
    bg_note = "AniList" if al_bg else "Kitsu" if kts_bg else "MyAnimeList"

    if post_note == bg_note:
        note += f"{post_note} for poster and background."
    else:
        note += f"{post_note} for poster"
        if bg_note != "MyAnimeList":
            note += f" and {bg_note} for background."
        else:
            note += "."

    # Build sendMessages
    tgs = []
    tgs.extend(genre.name for genre in jk_dat.genres)
    tgs.extend(genre.name for genre in jk_dat.themes)
    tgs.extend(genre.name for genre in jk_dat.demographics)
    content_warning = False
    tgs.extend(f"{genre.name} **!**" for genre in jk_dat.explicit_genres)
    if len(jk_dat.explicit_genres) > 0:
        content_warning = True

    ssonn = jk_dat.season
    daten = datetime(1970, 1, 1, tzinfo=timezone.utc)
    tgs = sorted(set(tgs), key=str.casefold)
    tgs = ", ".join(tgs) if tgs else "*None*"

    astn, aenn = jk_dat.aired.from_, jk_dat.aired.to
    year = str(astn.year) if astn else "year?"
    astr = jk_dat.aired.string
    bcast = jk_dat.broadcast

    # Grab studio names on jk_dat['studios'][n]['name']
    studio_names = [stud.name for stud in jk_dat.studios] if jk_dat.studios else None
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
                prop = jk_dat.aired.from_
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
                prop = jk_dat.aired.to
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
        if jk_dat.status == "Currently Airing":
            aen = "Ongoing"
        elif jk_dat.status == "Not yet aired" or astr == "Not available":
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
    elif jk_dat.aired.prop.from_.month is not None:
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
    rot = jk_dat.title
    nat = jk_dat.title_japanese or "*None*"
    ent = jk_dat.title_english
    english_note = False

    # Create a synonyms list
    syns = (
        [
            name.title
            for name in jk_dat.titles
            if name.type not in ["Default", "English"]
        ]
        if jk_dat.titles
        else []
    )
    if not ent or (ent == ""):
        # Set ent to a synonym in ASCII or the original title
        for name in syns:
            if re.match(r"([0-9a-zA-Z][:0-9a-zA-Z ]+)(?= )", name):
                ent = name
                break
        else:
            ent = rot
        english_note = True

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
    pvd = jk_dat.scored_by if jk_dat.scored_by else 0
    pvd = (
        f"{pvd:,} people voted"
        if pvd > 1
        else "1 person voted"
        if pvd == 1
        else "0 person voted"
    )

    # Format number of episodes
    eps = jk_dat.episodes if jk_dat.episodes else "*Unknown*"

    # Format status
    stat = jk_dat.status if jk_dat.status else "*Unknown*"

    # Format duration
    dur = jk_dat.duration if jk_dat.duration else "*Unknown*"

    # Format score
    scr = jk_dat.score if jk_dat.score else "0"

    if english_note:
        footnote = "\n* Data might be inaccurate due to bot rules/config, please check source for more information."
    else:
        footnote = ""

    if content_warning:
        content_warning_note = '\n* Some tags marked with "!" are NSFW.'
    else:
        content_warning_note = ""

    note = f"{content_warning_note}{footnote}"

    if str(eps) in ["1", "0", None]:
        eps_field = EmbedField(name="Duration", value=f"{dur}", inline=True)
    else:
        eps_field = EmbedField(name="Eps/Duration", value=f"{eps} ({dur})", inline=True)

    embed = Embed(
        author=EmbedAuthor(
            name="MyAnimeList Anime",
            url="https://myanimelist.net",
            icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png",
        ),
        title=rot,
        url=f"https://myanimelist.net/anime/{mal_id}",
        description=f"""-# `{mal_id}`, {jk_dat.type}, {sson} {year}, ⭐ {scr}/10 by {pvd}

> {cyno}
""",
        color=0x2E51A2,
        fields=[
            EmbedField(
                name=f"English Title{'*' if english_note else ''}",
                value=ent,
                inline=True,
            ),
            EmbedField(name="Native Title", value=nat, inline=True),
            EmbedField(name="Synonyms", value=syns),
            EmbedField(name="Genres and Themes", value=tgs),
            eps_field,
            EmbedField(name="Status", value=stat, inline=True),
            EmbedField(name="Studio", value=stdio, inline=True),
            EmbedField(name="Aired", value=date),
        ],  # type: ignore
        footer=EmbedFooter(text=note),
    )
    if poster is not None:
        embed.set_thumbnail(url=poster)
    if background is not None:
        embed.set_image(url=background)
    buttons: list[Button] = []
    if anime_api is not None:
        if anime_api.anilist is not None:
            ext_id = media_id_to_platform(f"{anime_api.anilist}", Platform.ANILIST)
            buttons.append(
                Button(
                    style=ButtonStyle.URL,
                    url=ext_id.uid,
                    emoji=PartialEmoji(id=ext_id.emoid, name="aniList"),
                )
            )
        if anime_api.kitsu is not None:
            ext_id = media_id_to_platform(f"{anime_api.kitsu}", Platform.KITSU)
            buttons.append(
                Button(
                    style=ButtonStyle.URL,
                    url=ext_id.uid,
                    emoji=PartialEmoji(id=ext_id.emoid, name="kitsu"),
                )
            )
        if anime_api.anidb is not None:
            ext_id = media_id_to_platform(f"{anime_api.anidb}", Platform.ANIDB)
            buttons.append(
                Button(
                    style=ButtonStyle.URL,
                    url=ext_id.uid,
                    emoji=PartialEmoji(id=ext_id.emoid, name="anidb"),
                )
            )
        if anime_api.animenewsnetwork is not None:
            ext_id = media_id_to_platform(
                f"{anime_api.animenewsnetwork}", Platform.ANIMENEWSNETWORK
            )
            buttons.append(
                Button(
                    style=ButtonStyle.URL,
                    url=ext_id.uid,
                    emoji=PartialEmoji(id=ext_id.emoid, name="animenewsnetwork"),
                )
            )
        if anime_api.simkl is not None:
            ext_id = media_id_to_platform(f"{anime_api.simkl}", Platform.SIMKL, "anime")
            buttons.append(
                Button(
                    style=ButtonStyle.URL,
                    url=ext_id.uid,
                    emoji=PartialEmoji(id=ext_id.emoid, name="simkl"),
                )
            )
    anime_stats: Button = Button(
        style=ButtonStyle.URL,
        label="Anime Stats",
        url=f"https://anime-stats.net/anime/show/{quote(rot)}",
    )
    themes_moe: Button = Button(
        style=ButtonStyle.URL,
        label="AnimeThemes",
        url=f"https://animethemes.moe/anime/{generate_animethemes_slug(rot)}",
    )
    ext_id = media_id_to_platform(f"{mal_id}", Platform.SHIKIMORI)
    shiki_button = Button(
        style=ButtonStyle.URL,
        url=ext_id.uid,
        emoji=PartialEmoji(id=ext_id.emoid, name="shikimori"),
    )
    buttons.extend([shiki_button, anime_stats, themes_moe])

    return (embed, buttons)


async def mal_submit(
    ctx: SlashContext | ComponentContext | Message,
    ani_id: int,
    replace: bool = False,
) -> None:
    """
    Send anime information from MAL to the channel

    Args:
        ctx (SlashContext | ComponentContext | Message): The context of the command
        ani_id (int): The anime ID
        replace (bool, optional): Whether to replace the original message. Defaults to False.

    Raises:
        *None*
    """
    nsfw_bool = await get_nsfw_status(ctx)
    trailer: Button | None = None

    try:
        async with AnimeApi() as aniapi:
            animeapi = await aniapi.get_relation(
                media_id=ani_id, platform=aniapi.AnimeApiPlatforms.MYANIMELIST
            )

        al_data: AniListMediaStruct | None = None
        embed: Embed
        buttons: list[Button] = []

        if animeapi.anilist is not None:
            async with AniList() as anilist:
                try:
                    al_data = await anilist.anime(media_id=animeapi.anilist)
                except ProviderHttpError:
                    al_data = None

                if al_data is not None and al_data.trailer is not None:
                    trailer = generate_trailer(data=al_data.trailer)
        else:
            al_data = AniListMediaStruct(id=0)

        embed, buttons = await generate_mal(
            ani_id, is_nsfw=nsfw_bool, anilist_data=al_data, anime_api=animeapi
        )
        if trailer is not None:
            buttons.append(trailer)
        # split to 5x5 buttons, unlabeled buttons should be at first
        final_buttons: list[ActionRow] = []
        unlabeled_buttons: list[Button] = []
        labeled_buttons: list[Button] = []
        for button in buttons:
            if button.label is None:
                unlabeled_buttons.append(button)
            else:
                labeled_buttons.append(button)
        for i in range(0, len(unlabeled_buttons), 5):
            final_buttons.append(ActionRow(*unlabeled_buttons[i : i + 5]))
        for i in range(0, len(labeled_buttons), 5):
            final_buttons.append(ActionRow(*labeled_buttons[i : i + 5]))
        await send_or_edit_message(ctx, embed, final_buttons, replace)
        return

    except MediaIsNsfw as err:
        notice = err.args[0] if err.args else ""
        embed = platform_exception_embed(
            description=f"I detected if this title is NSFW. {notice}",
            error="Media is NSFW",
            error_type=PlatformErrType.NSFW,
        )
        await send_or_edit_message(ctx, embed, None, replace)
        save_traceback_to_file("anilist", ctx.author, err)
    # pylint: disable=broad-exception-caught
    except Exception as err:
        embed = generate_commons_except_embed(
            description="We are unable to get the anime information from MyAnimeList via Jikan",
            error=f"{err}",
        )
        await send_or_edit_message(ctx, embed, None, replace)
        save_traceback_to_file("jikan", ctx.author, err)
