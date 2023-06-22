import html
import re
from datetime import datetime, timezone
from typing import Any, Literal

from interactions import (Button, ButtonStyle, ComponentContext, Embed,
                          EmbedAuthor, EmbedField, PartialEmoji, SlashContext)

from classes.anilist import AniList, AniListMediaStruct
from classes.excepts import MediaIsNsfw, ProviderHttpError
from modules.commons import (PlatformErrType, convert_html_to_markdown,
                             generate_trailer, get_nsfw_status,
                             platform_exception_embed, sanitize_markdown,
                             save_traceback_to_file, trim_synopsis)
from modules.const import MESSAGE_WARN_CONTENTS, banned_tags
from modules.i18n import fetch_language_data


async def search_al_anime(title: str) -> list[dict[str, Any]]:
    """
    Search anime via AniList API, formatted in MAL style

    Args:
        title (str): Title of the anime to search for

    Returns:
        list[dict[str, Any]]: The formatted data
    """
    async with AniList() as anilist:
        data = await anilist.search_media(
            title, limit=5, media_type=anilist.MediaType.ANIME
        )

    # Create an empty list to store the formatted data
    formatted_data: list[dict[str, Any]] = []

    # Loop through each item in the AniList response
    for item in data:
        if item["idMal"] in ["", "0", 0, None]:
            continue
        # Extract the relevant fields and format them
        formatted_item = {
            "node": {
                "id": item["idMal"],
                "title": item["title"]["romaji"],
                "alternative_titles": {
                    "en": item["title"]["english"] if item["title"]["english"] else "",
                    "ja": item["title"]["native"],
                },
                "start_season": {
                    "year": item["startDate"]["year"],
                    "season": item["season"].lower() if item["season"] else None,
                },
                "media_type": item["format"].lower() if item["format"] else None,
            }}
        # Append the formatted data to the list
        formatted_data.append(formatted_item)

    # Return the formatted data
    return formatted_data


def bypass_anilist_nsfw_tag(alm: AniListMediaStruct) -> bool:
    """Bypass adult rated tagged entry on AniList if it's only an Ecchi tag"""
    # get the genres
    tgs: list[str] = []
    if alm.genres is not None:
        tgs += list(alm.genres)
    if alm.tags is not None:
        tgs += [t.name for t in alm.tags]

    return "Ecchi" in tgs


async def generate_anilist(
    entry_id: int, is_nsfw: bool | None = False
) -> list[Embed, list[Button]]:
    """
    Generate an embed for an AniList entry, especially with manga

    Args:
        entry_id (int): The ID of the entry
        is_nsfw (bool, optional): Whether the channel/DM of invoked command does have NSFW enabled. Defaults to False.

    Returns:
        list[Embed, list[Button]]: The embed and the buttons
    """
    notice = MESSAGE_WARN_CONTENTS if is_nsfw is None else ""

    async with AniList() as anilist:
        alm = await anilist.manga(entry_id)

    bypass_ecchi = bypass_anilist_nsfw_tag(alm)
    if not bypass_ecchi:
        bypass_ecchi = not alm.isAdult

    if not (is_nsfw or bypass_ecchi):
        raise MediaIsNsfw(f"{notice}")

    media_id = entry_id
    mal_id = alm.idMal
    media_pg = alm.siteUrl if alm.siteUrl else f"https://anilist.co/manga/{media_id}"
    romaji = alm.title.romaji
    native = alm.title.native
    synonyms = alm.synonyms
    english = alm.title.english or next(
        (
            sys
            for sys in alm.synonyms or []
            if sys
            and re.match(r"([0-9a-zA-Z][:0-9a-zA-Z ]+)(?= )", sys)
            and sys is not None
        ),
        romaji,
    )
    if native is None:
        native = "*None*"
    english_note = english != alm.title.english

    original_titles = [romaji, native, english]
    synonyms = [
        val for val in synonyms if val not in original_titles and val is not None]
    synonyms = sorted(set(synonyms), key=str.casefold)
    synonyms_len = len(synonyms)
    syns = ""

    if synonyms_len > 8:
        syns_arr = synonyms[:8]
        syns = ", ".join(syns_arr)
        if (synonyms_len - 8) >= 1:
            syns += f", *and {synonyms_len - 8} more*"
    elif synonyms_len >= 1:
        syns = ", ".join(synonyms)
    else:
        syns = "*None*"

    description = alm.description
    if description is None:
        desc_done = "*None*"
    else:
        desc_done = html.unescape(description)
        desc_done = sanitize_markdown(desc_done)
        desc_done = (
            desc_done.replace("\\<", "<").replace(
                "\\>", ">").replace("\\/", "/")
        )
        desc_done = convert_html_to_markdown(desc_done)
        descs = desc_done.split("\n")
        synl = len(descs[0])
        desc_attr = f"\n> \n> Read more on [AniList]({media_pg})"

        if synl >= 1000:
            desc_done = trim_synopsis(descs[0])
        elif synl <= 150:
            desc_done = descs[0]
            if len(descs) >= 2:
                desc_done += "\n> \n> "
                for i in range(1, len(descs)):
                    if descs[i]:
                        desc_done += trim_synopsis(descs[i])
                        break
                if re.match(r"^(\(|\[)Source", desc_done) is not None:
                    desc_done += desc_attr
            else:
                desc_done += desc_attr
        else:
            desc_done = trim_synopsis(descs[0])

        if (
            desc_done[-3:] == "..."
            or (synl >= 150 and len(descs) > 3)
            or (synl >= 1000 and len(descs) > 1)
        ):
            desc_done += desc_attr

    poster = alm.coverImage.extraLarge
    hex_color = alm.coverImage.color if alm.coverImage.color else "#2E51A2"
    hex_color = int(hex_color.replace("#", ""), 16)
    banner = alm.bannerImage

    tgs = []
    content_warning = False
    sy_chk_mark = False
    for genre in alm.genres:
        tgs.append(genre)
    for tag in alm.tags:
        if tag is None:
            continue
        if tag.name not in banned_tags:
            if tag.isMediaSpoiler:
                tgs.append(f"||{tag.name}||")
            else:
                tgs.append(tag.name)
        elif tag.name in banned_tags and is_nsfw:
            if tag.isMediaSpoiler:
                tgs.append(f"||{tag.name} **!**||")
            else:
                tgs.append(f"{tag.name} **!** ")
            content_warning = True
        else:
            sy_chk_mark = True

    tags_formatted = ""
    if not tgs:
        tags_formatted = "*None*"
    elif len(tgs) > 20:
        sorted_tgs = sorted(set(tgs[:20]), key=str.casefold)
        tags_formatted = ", ".join(sorted_tgs)
        if (len(tgs) - 20) >= 1:
            tags_formatted += f", *and {len(tgs) - 20} more*"
    else:
        sorted_tgs = sorted(set(tgs), key=str.casefold)
        tags_formatted = ", ".join(sorted_tgs)

    format_raw: Literal["MANGA", "NOVEL", "ONE_SHOT"] | None = alm.format
    # lowercase the format
    match format_raw:
        case "ONE_SHOT":
            format_str = "One-shot"
        case None:
            format_str = "*Unknown*"
        case _:
            format_str = format_raw.capitalize()

    status_raw: Literal[
        "FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"
    ] | None = alm.status
    # lowercase the status
    match status_raw:
        case "NOT_YET_RELEASED":
            status = "Not yet released"
        case None:
            status = "*Unknown*"
        case _:
            status = status_raw.capitalize()

    chapters = f"{alm.chapters}" if alm.chapters else "*??*"
    volumes = f"{alm.volumes}" if alm.volumes else "*??*"

    average_score = alm.averageScore
    score_distribution = alm.stats["scoreDistribution"]
    total_score = 0
    people_voted = 0

    for item in score_distribution:
        total_score += item["score"] * item["amount"]
        people_voted += item["amount"]

    if average_score in [None, 0]:
        try:
            average_score = round(total_score / people_voted)
        except ZeroDivisionError:
            average_score = 0

    if (people_voted is None) or (people_voted == 0):
        people_voted = "0 person voted"
    elif people_voted > 1:
        people_voted = f"{people_voted:,} people voted"
        if average_score == 0:
            people_voted += " (UNSCORED)"
    elif people_voted == 1:
        people_voted = "1 person voted"

    year = "Unknown year"
    start_date = ""
    std_raw = alm.startDate
    if std_raw is not None:
        if std_raw.year:
            year = f"{std_raw.year}"
        if std_raw.year and std_raw.day and std_raw.month:
            std_dtime = datetime(
                std_raw.year, std_raw.month, std_raw.day, tzinfo=timezone.utc
            )
            start_date = f"<t:{int(std_dtime.timestamp())}:D>"
        else:
            start_date = "*Unknown*"

    end_date = ""
    end_raw = alm.endDate
    if end_raw is not None:
        if status == "Releasing":
            end_date = "Ongoing"
        elif end_raw.year and end_raw.day and end_raw.month and status == "Finished":
            end_dtime = datetime(
                end_raw.year, end_raw.month, end_raw.day, tzinfo=timezone.utc
            )
            end_date = f"<t:{int(end_dtime.timestamp())}:D>"
        else:
            end_date = start_date

    if english_note or sy_chk_mark:
        footnote = "\n* Data might be inaccurate due to bot rules/config, please check source for more information."
    else:
        footnote = ""

    if content_warning:
        content_warning_note = '\n* Some tags marked with "!" are NSFW.'
    else:
        content_warning_note = ""

    embed = Embed(
        author=EmbedAuthor(
            name="AniList Manga",
            url="https://anilist.co",
            icon_url="https://anilist.co/img/icons/android-chrome-192x192.png",
        ),
        title=romaji if romaji else native,
        url=media_pg,
        description=f"""*`{media_id}`*, {format_str}, {year}, ⭐ {average_score}/100, by {people_voted}

> {desc_done}""",
        color=hex_color,
        timestamp=datetime.now(timezone.utc),
        fields=[
            EmbedField(
                name=f"English Title{'*' if english_note else ''}",
                value=english if english else "*None*",
                inline=True,
            ),
            EmbedField(name="Native Title", value=native, inline=True),
            EmbedField(
                name="Synonyms",
                value=syns,
            ),
            EmbedField(
                name=f"Genres and Tags{'*' if sy_chk_mark else ''}",
                value=tags_formatted,
            ),
            EmbedField(name="Volumes", value=volumes, inline=True),
            EmbedField(name="Chapters", value=chapters, inline=True),
            EmbedField(name="Status", value=status, inline=True),
            EmbedField(
                name="Published",
                value=f"{start_date} - {end_date} ({start_date.replace('D', 'R')})",
            ),
        ],
    )

    if content_warning_note != "" or footnote != "":
        embed.set_footer(text=f"{content_warning_note}{footnote}")
    if poster:
        embed.set_thumbnail(url=poster)
    if banner:
        embed.set_image(url=banner)

    # buttons
    buttons: list[Button] = []
    if alm.trailer and alm.trailer.site == "youtube":
        trailer = generate_trailer(
            data=alm.trailer,
        )
        buttons.append(trailer)
    if mal_id:
        mal_button = Button(
            style=ButtonStyle.URL,
            label="MyAnimeList",
            url=f"https://myanimelist.net/manga/{mal_id}",
            emoji=PartialEmoji(id=1073442204921643048, name="myAnimeList"),
        )
        shikimori_button = Button(
            style=ButtonStyle.URL,
            label="Shikimori",
            url=f"https://shikimori.me/mangas/{mal_id}",
            emoji=PartialEmoji(id=1073441855645155468, name="shikimori"),
        )
        buttons.extend([mal_button, shikimori_button])

    return [embed, buttons]


async def anilist_submit(ctx: SlashContext | ComponentContext, media_id: int) -> None:
    """
    Submit a query to AniList API and send the result to the channel.

    Args:
        ctx (SlashContext | ComponentContext): The context of the command.
        media_id (int): The media ID to query.

    Raises:
        MediaIsNsfw: If the media is NSFW and the channel is not NSFW enabled.
        ProviderHttpError: If the API provider returns an error.

    Returns:
        None
    """
    buttons = []
    l_ = fetch_language_data(code="en_US")
    try:
        nsfw_bool = await get_nsfw_status(ctx)
        embed, button_2 = await generate_anilist(
            entry_id=media_id,
            is_nsfw=nsfw_bool,
        )
        buttons.extend(button_2)
        await ctx.send(embed=embed, components=buttons)
        return

    except MediaIsNsfw as e:
        notice = e.args[0] if e.args else ""
        embed = platform_exception_embed(
            description="This media is NSFW, please invoke the same query on NSFW enabled channel.",
            error="Media is NSFW\n" + notice,
            lang_dict=l_,
            error_type=PlatformErrType.NSFW,
        )
        await ctx.send(embed=embed)
        save_traceback_to_file("anilist", ctx.author, e)

    except ProviderHttpError as e:
        message = e.message

        embed = platform_exception_embed(
            description="AniList API is currently unavailable, please try again later.",
            error=f"{message}",
            lang_dict=l_,
            error_type=PlatformErrType.SYSTEM,
        )
        await ctx.send(embed=embed)
        save_traceback_to_file("anilist", ctx.author, e)
