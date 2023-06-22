import re

from interactions import (Button, ButtonStyle, ComponentContext, Embed,
                          EmbedAuthor, EmbedField, SlashContext)

from classes.excepts import ProviderHttpError
from classes.rawg import RawgApi, RawgGameData
from modules.commons import (PlatformErrType, platform_exception_embed,
                             sanitize_markdown, save_traceback_to_file,
                             trim_synopsis)
from modules.i18n import fetch_language_data


async def generate_rawg(data: RawgGameData) -> list[Embed, list[Button]]:
    """
    Generate embed for RAWG API

    Args:
        data (RawgGameData): RAWG API data

    Returns:
        list[Embed, Button]: Embed and button
    """
    # Extract data from the input object
    id = data.slug

    # Process alternative names
    syns = sorted(set(data.alternative_names) -
                  {data.name, data.name_original}, key=str.casefold)
    syns = syns[:8] if len(syns) > 8 else syns
    syns_text = ", ".join(syns) if syns else "*None*"
    if len(syns) < len(data.alternative_names):
        syns_text += f", *and {len(data.alternative_names) - len(syns)} more*"

    # Process platforms
    pfs = sorted({pf.platform.name for pf in data.platforms}, key=str.casefold)
    pfs_text = ", ".join(pfs)

    # Process ratings
    scr = data.rating or 0
    mc_scr = data.metacritic or 0

    # Process ESRB rating
    rte = data.esrb_rating.name if data.esrb_rating else "Unknown Rating"

    # Process developers
    devs = sorted({d.name for d in data.developers}, key=str.casefold)
    devs_text = ", ".join(devs) if devs else "*None*"

    # Process publishers
    pubs = sorted({p.name for p in data.publishers}, key=str.casefold)
    pubs_text = ", ".join(pubs) if pubs else "*None*"

    # Process game description
    description = data.description_raw
    if description is None:
        cyno = "*None*"
    else:
        cyno = sanitize_markdown(description)
        descs = cyno.split("\n")
        synl = len(descs[0])
        desc_attr = f"\n> \n> [Read more on RAWG](https://rawg.io/games/{id})"

        if synl >= 1000:
            cyno = trim_synopsis(descs[0])
        elif synl <= 150:
            cyno = descs[0]
            if len(descs) >= 2:
                for i in range(1, len(descs)):
                    if descs[i] not in ["", " "]:
                        cyno += "\n> \n> "
                        cyno += trim_synopsis(descs[i])
                        break
            else:
                cyno += desc_attr
        else:
            cyno = trim_synopsis(descs[0])

        if (
            cyno.endswith("...")
            or (synl >= 150 and len(descs) > 2)
            or (synl >= 1000 and len(descs) > 1)
        ):
            cyno += desc_attr

    # Process genres and tags
    tgs = sorted({g.name.title()
                 for g in data.genres + data.tags}, key=str.casefold)
    tgs_text = (
        ", ".join(tgs[:20]) if len(tgs) > 20 else ", ".join(
            tgs) if tgs else "*None*"
    )
    if len(tgs) > 20:
        lefties = len(tgs) - 20
        if lefties >= 1:
            tgs_text += f", *and {lefties} more*"

    # Process release date
    rel = "Unknown year"
    if not data.tba and data.released is not None:
        year = data.released.strftime("%Y")
        rel = f"<t:{int(data.released.timestamp())}:D> (<t:{int(data.released.timestamp())}:R>)"

    # Process additional links
    pdt = []
    if data.website:
        pdt.append({"name": "Website", "value": data.website})
    if data.metacritic_url:
        pdt.append({"name": "Metacritic", "value": data.metacritic_url})
    if data.reddit_url:
        reddit = data.reddit_url
        if re.match(r"^http(s)?://(www.)?reddit.com/r/(\w+)", reddit):
            subreddit = reddit
        elif re.match(r"r/(\w+)", reddit):
            subreddit = f"https://reddit.com/{reddit}"
        elif re.match(r"^(\w+)", reddit):
            subreddit = f"https://reddit.com/r/{reddit}"
        pdt.append({"name": "Reddit", "value": subreddit})

    # Create button components
    components = [
        Button(
            style=ButtonStyle.URL,
            label=p["name"],
            url=p["value"]) for p in pdt]

    # Create the embed
    embed = Embed(
        author=EmbedAuthor(
            name="RAWG Game",
            url="https://rawg.io/",
            icon_url="https://pbs.twimg.com/profile_images/951372339199045632/-JTt60iX_400x400.jpg",
        ),
        title=data.name,
        url=f"https://rawg.io/games/{id}",
        description=f"*{rte}, {year}, ⭐ {scr}/5 (Metacritic: {mc_scr})*\n\n> {cyno}",
        color=0x1F1F1F,
        fields=[
            EmbedField(
                name="English Title",
                value=data.name,
                inline=True),
            EmbedField(
                name="Native Title",
                value=data.name_original,
                inline=True),
            EmbedField(
                name="Synonyms",
                value=syns_text,
                inline=False),
            EmbedField(
                name="Genres and Tags",
                value=tgs_text,
                inline=False),
            EmbedField(
                name="Platforms",
                value=pfs_text,
                inline=False),
            EmbedField(
                name="Developers",
                value=devs_text,
                inline=True),
            EmbedField(
                name="Publishers",
                value=pubs_text,
                inline=True),
            EmbedField(
                name="Release Date",
                value=rel,
                inline=True),
        ],
    )
    embed.set_image(url=data.background_image)
    return [embed, components]


async def rawg_submit(ctx: SlashContext | ComponentContext, slug: str) -> None:
    """
    Submit a query to the RAWG API and return the result as an embed.

    Args:
        ctx (SlashContext | ComponentContext): The context of the command.
        slug (str): The slug of the game to search for.

    Raises:
        ProviderHttpError: If the API returns an error.

    Returns:
        None
    """
    buttons = []
    l_ = fetch_language_data(code="en_US")
    try:
        async with RawgApi() as api:
            game_data = await api.get_data(slug)
        embed, button_2 = await generate_rawg(data=game_data)
        buttons.extend(button_2)
        await ctx.send(embed=embed, components=buttons)
        return
    except ProviderHttpError as e:
        status = e.status_code
        message = e.message

        embed = platform_exception_embed(
            description="AniList API is currently unavailable, please try again later.",
            error=f"HTTP Error {status}\n{message}",
            lang_dict=l_,
            error_type=PlatformErrType.SYSTEM,
        )
        await ctx.send(embed=embed)
        save_traceback_to_file("rawg", ctx.author, e)
