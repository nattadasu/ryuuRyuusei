from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal

import interactions as ipy

from classes.excepts import MediaIsNsfw, ProviderHttpError
from classes.simkl import Simkl
from classes.tmdb import TheMovieDb
from modules.commons import (PlatformErrType, generate_trailer,
                             get_nsfw_status, platform_exception_embed,
                             save_traceback_to_file, trim_synopsis)
from modules.const import MESSAGE_WARN_CONTENTS
from modules.platforms import Platform, media_id_to_platform


async def create_simkl_embed(
    data: dict[str, Any],
    media_type: Literal["tv", "movies"],
    is_channel_nsfw: bool | None = None,
    is_media_nsfw: bool | None = None,
) -> tuple[ipy.Embed, list[ipy.ActionRow | ipy.Button]]:
    """
    Generate embed for Simkl API

    Args:
        data (Dict[str, any]): Simkl API data
        media_type (Literal['tv', 'movies']): Media type
        is_chnnel_nsfw (bool, optional): Whether the channel is NSFW, defaults to None
        is_media_nsfw (bool, optional): Whether the media is NSFW, defaults to None

    Returns:
        list[Embed, list[ActionRow | Button]]: The embed and the buttons
    """
    notice = MESSAGE_WARN_CONTENTS if is_channel_nsfw is None else ""

    if is_media_nsfw is True and is_channel_nsfw is False:
        raise MediaIsNsfw(notice)

    media_id = str(data["ids"]["simkl"])
    title = data.get("title", None)
    synonyms = data.get("alt_titles", None)
    status: str | None = data.get("status", None)
    match status:
        case None:
            status = ""
        case "tba":
            status = ", To Be Announced"
        case _:
            status = f", {status.capitalize()}"
    scores: dict[str, dict[str, int | float]
                 ] | None = data.get("ratings", None)
    certification = data.get("certification", None)
    country = data.get("country", None)
    network = data.get("network", None)
    runtime = data.get("runtime", None)
    airing_date = None

    # Process synonyms
    if synonyms is None:
        synonyms = "*None*"
    else:
        synonyms = [x["name"] for x in synonyms if x["name"] != title]
        synonyms = sorted(set(synonyms), key=str.casefold)
        len_synonyms = len(synonyms)

        if len_synonyms > 8:
            synonyms = synonyms[:8]
            count_syn = len_synonyms - 8
            if count_syn > 0:
                synonyms.append(f"*and {count_syn} more*")
            synonyms = ", ".join(synonyms)
        elif len_synonyms > 1:
            synonyms = ", ".join(synonyms)
        elif len_synonyms == 1:
            synonyms = synonyms[0]

    # Process eps
    episodes = data.get("total_episodes", None)
    if episodes is None:
        episodes = "*??*"

    # Process runtime
    if runtime is not None:
        runtime = f"({runtime} mins/eps)" if media_type == "tv" else f"{runtime} mins"
    else:
        runtime = "*Unknown*"

    # Process country
    if country is not None:  # type: ignore
        country: str = f"{country.upper()} :flag_{country.lower()}:"
    else:
        country = "*Unknown*"

    airing = ""
    release = ""

    # Process start date
    if media_type == "tv":
        airing_date = data.get("first_aired", None)
        if airing_date in ["", None]:
            airing = "TBA"
            time_since_release = ""
            airing_date = None
        else:
            if airing_date.endswith("Z"):
                airing_date = airing_date[:-1] + "+00:00"
            else:
                airing_date += "T00:00:00+00:00"
            airing = datetime.strptime(airing_date, "%Y-%m-%dT%H:%M:%S%z")
            time_since_release = f"(<t:{int(airing.timestamp())}:R>)"
            airing_date = airing
            airing = f"<t:{int(airing.timestamp())}:D>"
    elif media_type == "movies":
        release_date = data.get("released", None)
        if release_date in ["", None]:
            release = "TBA"
            time_since_release = ""
            release_date = None
        else:
            release_date += "T00:00:00+00:00"
            release = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S%z")
            time_since_release = f"(<t:{int(release.timestamp())}:R>)"
            release_date = release
            release = f"<t:{int(release.timestamp())}:D>"

    year = data.get("year", None)
    end_date: str | None = None
    season: int = 1
    eps_data: list[dict[str, str | int | dict[str, str | int]]] = []

    if media_type == "tv":
        try:
            async with Simkl() as simkl:
                eps_data: list[dict[str, str | int | dict[str, str | int]]] = await simkl.get_show_episodes(media_id)
            eps_data = [x for x in eps_data if x["type"] != "special"]
            eps_data.reverse()
            if len(eps_data) > 0:
                season = eps_data[0].get("season", 1)  # type: ignore
                end_date = eps_data[0].get("date", None)  # type: ignore
        except ProviderHttpError:
            # do nothing
            pass

    # Process end date
    # take episode information if its a show and haven't ended yet
    if episodes != "*??*" and airing_date is not None and len(eps_data) > 0 and end_date is not None:
        # grab "date", and format it
        guess_date = datetime.fromisoformat(end_date)
        end_date = f"<t:{int(guess_date.timestamp())}:D>"
    elif episodes != "*??*" and airing_date is not None and status == ", Ended":
        guess_date = airing_date + timedelta(weeks=episodes)
        end_date = f"<t:{int(guess_date.timestamp())}:D>\\*"
    elif status == ", Airing":
        end_date = "TBA"
    elif status == ", To Be Announced":
        end_date = "TBA"
    else:
        end_date = "*Unknown*"

    if time_since_release not in ["", None]:
        time_since_release = " " + time_since_release

    if media_type == "tv":
        if airing == "TBA" and end_date == "TBA":
            date = "TBA"
        else:
            date = f"{airing} - {end_date}{time_since_release}"
    elif media_type == "movies":
        date = f"{release}{time_since_release}"

    # Process description
    description = data.get("overview", None)
    if not description:
        description = "*No description provided*"
    else:
        description = description.replace("\r", "")
        description = description.split("\n")
        description_length = len(description)
        first_line = description[0]
        more_link = (
            f"\n> \n> [Read more on SIMKL](https://simkl.com/{media_type}/{media_id})"
        )

        if len(first_line) >= 1000:
            trimmed_description = trim_synopsis(first_line)
        elif len(first_line) <= 150:
            trimmed_description = first_line
            if description_length > 1:
                trimmed_description += "\n> \n> "
                for line in description[1:]:
                    if line not in ("", None):
                        trimmed_description += trim_synopsis(line)
        else:
            trimmed_description = first_line

        if (
            trimmed_description[-3:] == "..."
            or (description_length >= 150 and len(description) > 3)
            or (description_length >= 1000 and len(description) > 1)
        ):
            trimmed_description += more_link

        description = trimmed_description

    score = 0
    votes = 0
    if scores is not None:
        mock = {"rating": 0, "votes": 0}
        simkl_score: dict[str, int | float] = scores.get(
            "simkl", mock)  # type: ignore
        score = simkl_score.get("rating", 0)
        votes = simkl_score.get("votes", 0)

    # Process genres
    genres = data.get("genres", [])
    if genres is None:
        genres = []
    if len(genres) == 0:
        genres = "*None*"
    elif len(genres) > 20:
        sorted_genres = sorted(set(genres[:20]), key=str.casefold)
        genres = ", ".join(sorted_genres)
        if (len(genres) - 20) >= 1:
            genres += f", and {len(genres - 20)} more"
    else:
        sorted_genres = sorted(set(genres), key=str.casefold)
        genres = ", ".join(sorted_genres)

    # Process poster and fanart
    poster = data.get("poster", None)
    fanart = data.get("fanart", None)

    embed = ipy.Embed(
        author=ipy.EmbedAuthor(
            name=f"SIMKL {'TV' if media_type == 'tv' else 'Movie'}",
            url="https://simkl.com",
            icon_url="https://media.discordapp.net/attachments/1078005713349115964/1094570318967865424/ico_square_1536x1536.png",
        ),
        title=title,
        url=f"https://simkl.com/{media_type}/{media_id}",
        description=f"""-# `{media_id}`, {'TV' if media_type =='tv' else 'Movies'}{status}, {year}, ⭐ {score}/10 by {votes:,} {'people' if votes >= 2 else 'person'}

> {description}""",
        color=0x0B0F10,
        timestamp=datetime.now(tz=timezone.utc),
    )

    if poster is not None:
        embed.set_thumbnail(url=f"https://simkl.in/posters/{poster}_m.webp")
    if fanart is not None:
        embed.set_image(url=f"https://simkl.in/fanart/{fanart}_w.webp")

    embed.add_field(name="Synonyms", value=synonyms or "*None*", inline=False)
    embed.add_field(name="Genres", value=genres, inline=False)
    if media_type == "tv":
        embed.add_field(name="Network", value=network or "*None*", inline=True)
    embed.add_field(name="Certification",
                    value=certification or "*None*", inline=True)
    embed.add_field(name="Country", value=country, inline=True)
    embed.add_field(
        name="Episodes and Duration" if media_type == "tv" else "Duration",
        value=f"{episodes} {runtime}" if media_type == "tv" else f"{runtime}",
        inline=True,
    )
    if media_type == "tv":
        embed.add_field(name="Seasons", value=season, inline=True)
    embed.add_field(
        name="Airing Date" if media_type == "tv" else "Release Date",
        value=date,
        inline=True,
    )

    if end_date.endswith("\\*"):
        embed.set_footer(
            text="* This is estimated end date (as SIMKL didn't provide end date well), please take the info with a pinch of salt")

    buttons: list[ipy.Button] = []

    ids = data.get("ids", {})

    platforms = [
        {
            "name": "imdb",
            "url": ids.get("imdb", None),
        },
        {
            "name": "tmdb",
            "url": f"{'tv' if media_type == 'tv' else 'movie'}/{ids.get('tmdb', '')}"
            if ids.get("tmdb", None)
            else None,
        },
        {
            "name": "tvdbslug",
            "url": f"https://www.thetvdb.com/series/{ids.get('tvdbslug', '')}"
            if ids.get("tvdbslug", None)
            else f"https://www.thetvdb.com/movies/{ids.get('tvdbmslug', '')}"
            if ids.get("tvdbslug", None)
            else None,
        },
        {
            "name": "tvdb",
            "url": f"https://www.thetvdb.com/deferrer/{'series' if media_type == 'tv' else 'movies'}/{ids.get('tvdbslug', '')}"
            if ids.get("tvdb", None)
            else None,
        },
        {
            "name": "trakt",
            # use IMDB's for auto-redirect from Trakt end, and media type from SIMKL
            "url": f"search/imdb/{ids.get('imdb', '')}?type={'shows' if media_type == 'tv' else 'movies'}"
            if ids.get("imdb", None)
            else None,
        }
    ]
    # if tvdbslug's url is not available, use tvdb's url instead
    if platforms[2]["url"] is not None:
        del platforms[3]
    elif platforms[3]["url"] is not None:
        del platforms[2]
    for platform in platforms:
        if platform["url"] is not None:
            platform_name = platform["name"]
            if platform_name == "tvdbslug":
                platform_name = "tvdb"
            pf = media_id_to_platform(platform["url"], Platform(platform_name))
        else:
            continue
        pfn: dict[str, str] = {
            "imdb": "IMDb",
            "tmdb": "tmdb",
            "tvdb": "tvdb",
            "trakt": "trakt",
        }
        buttons.append(
            ipy.Button(
                style=ipy.ButtonStyle.LINK,
                url=pf.uid,
                emoji=ipy.PartialEmoji(
                    id=pf.emoid, name=pfn[platform_name]),
            )
        )

    if data.get("trailers", None) is not None:
        try:
            trailer = generate_trailer(data["trailers"][0], is_mal=False)
        except IndexError:
            trailer = None

        if trailer is not None:
            buttons.append(trailer)

    return [embed, buttons]


async def simkl_submit(
    ctx: ipy.SlashContext | ipy.ComponentContext | ipy.Message,
    media_id: int | str,
    media_type: Literal["tv", "movies"] = "tv",
) -> None:
    """
    Smbit a query to SIMKL and send the result to the channel

    Args:
        ctx (ipy.SlashContext | ipy.ComponentContext | ipy.Message): The context of the command
        media_id (int | str): The ID of the media
        media_type (Literal['tv', 'movies'], optional): The type of the media. Defaults to 'tv'.
    """
    buttons = []
    try:
        async with Simkl() as simkl:
            if media_type == "tv":
                data: dict[str, Any] = await simkl.get_show(f"{media_id}")
            else:
                data: dict[str, Any] = await simkl.get_movie(f"{media_id}")

        tmdb_id = data.get("ids", {"tmdb": None}).get("tmdb", None)
        if tmdb_id is not None:
            try:
                async with TheMovieDb() as tmdb:
                    media_nsfw: bool = await tmdb.get_nsfw_status(
                        tmdb_id,
                        tmdb.MediaType.TV
                        if media_type == "tv"
                        else tmdb.MediaType.MOVIE,
                    )
            except ProviderHttpError:
                media_nsfw = False
        else:
            media_nsfw = False

        channel_nsfw = await get_nsfw_status(ctx)
        embed, button_2 = await create_simkl_embed(
            data=data,
            media_type=media_type,
            is_channel_nsfw=channel_nsfw,
            is_media_nsfw=media_nsfw,
        )
        buttons.append(button_2)
        if isinstance(ctx, ipy.Message):
            await ctx.reply(embed=embed, components=buttons)  # type: ignore
        else:
            await ctx.send(embed=embed, components=buttons)
        return

    except MediaIsNsfw as err:
        notice = err.args[0] if err.args else ""
        embed = platform_exception_embed(
            description="This media is NSFW, please invoke the same query on NSFW enabled channel.",
            error="Media is NSFW\n" + notice,
            error_type=PlatformErrType.NSFW,
        )
        if isinstance(ctx, ipy.Message):
            await ctx.reply(embed=embed)
        else:
            await ctx.send(embed=embed)
        save_traceback_to_file("simkl", ctx.author, err)

    except ProviderHttpError as err:
        status = err.status_code
        message = err.message

        embed = platform_exception_embed(
            description="SIMKL API is currently unavailable, please try again later.",
            error=f"HTTP Error {status}\n{message}",
            error_type=PlatformErrType.SYSTEM,
        )
        if isinstance(ctx, ipy.Message):
            await ctx.reply(embed=embed)
        else:
            await ctx.send(embed=embed)
        save_traceback_to_file("simkl", ctx.author, err)
