from classes.anilist import AniList


async def search_al_anime(title: str) -> dict:
    """
    Search anime via AniList API, formatted in MAL style

    Args:
        title (str): Title of the anime to search for

    Returns:
        dict: The formatted data
    """
    async with AniList() as anilist:
        data = await anilist.search_media(
            title, limit=5, media_type=anilist.MediaType.ANIME
        )

    # Create an empty list to store the formatted data
    formatted_data = []

    # Loop through each item in the AniList response
    for item in data:
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
            }
        }
        # Append the formatted data to the list
        formatted_data.append(formatted_item)

    # Return the formatted data
    return formatted_data


async def bypass_anilist_nsfw_tag(alm: AniListMediaStruct) -> bool:
    """Bypass adult rated tagged entry on AniList if it's only an Ecchi tag"""
    # get the genres
    tgs = []
    if alm.genres is not None:
        tgs += [g for g in alm.genres]
    if alm.tags is not None:
        tgs += [t.name for t in alm.tags]

    if None in tgs:
        tgs.remove(None)

    if "Ecchi" in tgs:
        return True
    else:
        return False
