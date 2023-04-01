from modules.commons import *


async def searchAniList(name: str = None, isAnime: bool = True) -> dict:
    """Search anime on AniList"""
    try:
        url = 'https://graphql.anilist.co'
        mediaType = 'ANIME' if isAnime else 'MANGA'
        variables = {
            'mediaType': mediaType.upper()
        }
        qs = '''query ($search: String, $mediaType: MediaType) {'''
        result = '''results: media(type: $mediaType, search: $search) {'''
        variables['search'] = name

        query = f'''{qs}
    {mediaType.lower()}: Page(perPage: 5) {{
        {result}
            id
            idMal
            title {{
                romaji
                english
                native
            }}
            isAdult
            format
            status
            bannerImage
            averageScore
        }}
    }}
}}'''
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query': query, 'variables': variables}) as resp:
                jsonResult = await resp.json()
            await session.close()
            return jsonResult['data'][f'{mediaType.lower()}']['results']
    except IndexError as ierr:
        raise Exception(ierr)


async def getAniList(media_id: int, isAnime: bool = True) -> dict:
    """Fetch the information regarding the title on AniList"""
    try:
        url = 'https://graphql.anilist.co'
        mediaType = 'ANIME' if isAnime else 'MANGA'
        variables = {
            'mediaType': mediaType.upper()
        }
        qs = '''query ($mediaId: Int, $mediaType: MediaType) {'''
        result = '''results: media(type: $mediaType, id: $mediaId) {'''
        variables['mediaId'] = media_id
        query = f'''{qs}
    {mediaType.lower()}: Page(perPage: 1) {{
        {result}
            id
            idMal
            title {{
                romaji
                english
                native
            }}
            isAdult
            description(asHtml: false)
            synonyms
            format
            startDate {{
                year
                month
                day
            }}
            endDate {{
                year
                month
                day
            }}
            status
            chapters
            volumes
            coverImage {{
                large
                extraLarge
            }}
            bannerImage
            genres
            tags {{
                name
                isMediaSpoiler
            }}
            averageScore
            stats {{
                scoreDistribution {{
                    score
                    amount
                }}
            }}
            trailer {{
                id
                site
            }}
        }}
    }}
}}'''
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query': query, 'variables': variables}) as resp:
                jsonResult = await resp.json()
            await session.close()
            return jsonResult['data'][f'{mediaType.lower()}']['results']
    except IndexError as ierr:
        raise Exception(ierr)


async def generateAnilist(alm: dict, isNsfw: bool = False, bypassEcchi: bool = False) -> interactions.Embed:
    """Generate an embed for Anilist manga."""
    if isNsfw is None:
        msgForThread = warnThreadCW
    else:
        msgForThread = ''
    byE = bypassEcchi
    if byE is not True:
        if alm['isAdult'] is True:
            byE = False
        else:
            byE = True
    else:
        byE = True
    if (isNsfw is not True) and (byE is False):
        raise Exception(
            f'{EMOJI_FORBIDDEN} **NSFW content is not allowed!**\nOnly NSFW channels are allowed to search NSFW content.{msgForThread}')
    m = alm['idMal']
    id = alm['id']
    rot = alm['title']['romaji']
    syns = alm['synonyms']
    ent = alm['title']['english']
    if ent is None:
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
        else:
            ent = rot
        enChkMark = '\\*'
    else:
        enChkMark = ''
    nat = alm['title']['native']
    if nat is None:
        nat = "*None*"

    ogt = [rot, ent, nat]
    syns = [x for x in syns if x not in ogt]
    # sort
    syns = sorted(set(syns), key=str.casefold)
    synsl = len(syns)

    if synsl > 8:
        syns = syns[:8]
        syns = ", ".join(syns)
        syns += f", *and {synsl - 8} more*"
    elif synsl > 1:
        syns = ", ".join(syns)
    elif synsl == 1:
        syns = syns[0]
    else:
        syns = "*None*"

    form = alm['format']
    # Only capitalize the first letter, rest must lowercase
    form = form[0].upper() + form[1:].lower()
    year = alm['startDate']['year']
    if year is None:
        year = "Unknown year"

    # grab score distribution
    scr = alm['averageScore']
    if scr is None:
        scr = 0
    scrDist = alm['stats']['scoreDistribution']
    pvd = 0
    for p in scrDist:
        pvd += pvd + p['amount']

    if (pvd is None) or (pvd == 0):
        pvd = "0 person voted"
    elif pvd > 1:
        pvd = f"{pvd:,} people voted"
        if scr == 0:
            pvd += " (UNSCORED)"
    elif pvd == 1:
        pvd = f"1 person voted"

    poster = alm['coverImage']['extraLarge']
    background = alm['bannerImage']

    if poster is None:
        poster = ""
    else:
        poster = poster.replace('http://', 'https://')

    if background is None:
        background = ""
    else:
        background = background.replace('http://', 'https://')

    # get the description
    cyno = alm['description']
    # convert html tags to markdown
    if cyno is not None:
        cyno = cyno.replace('\n', '').replace(
            '<i>', '*').replace('</i>', '*').replace('<br>', '\n').replace('<Br>', '\n').replace(
            '<b>', '**').replace('</b>', '**').replace('<strong>', '**').replace(
            '</strong>', '**').replace('<em>', '*').replace('</em>', '*').replace(
            '<u>', '__').replace('</u>', '__').replace('<strike>', '~~').replace(
            '</strike>', '~~').replace('<s>', '~~').replace('</s>', '~~').replace('<BR>', '\n')
        cyno = cyno.split('\n')
        cynl = len(cyno)

        cynoin = cyno[0]
        cynmo = f"\n> \n> [Read more on AniList](<https://anilist.co/manga/{id}>)"

        if len(str(cynoin)) <= 150:
            daff = cynoin
            if cynl >= 2:
                daff = cynoin
                for i in range(1, cynl + 1):
                    if (len(str(cyno[i])) > 0) or (cyno[i] != ""):
                        cynoAdd = cyno[i]
                        cynoAdd = sanitizeMarkdown(cynoAdd)
                        break
                cyno = trimCyno(daff)
                if re.match(r'^(\(|\[)Source', cynoAdd) != None:
                    cyno += "\n> \n> "
                    cyno += trimCyno(cynoAdd)
        elif len(str(cynoin)) >= 1000:
            cyno = trimCyno(cynoin)
        else:
            cyno = cynoin

        if (cyno[-3:] == "...") or ((len(str(cynoin)) >= 150) and (cynl > 3)) or ((len(str(cynoin)) >= 1000) and (cynl > 1)):
            cyno += cynmo
    else:
        cyno = "*None*"

    pdta = []
    if m is not None:
        pdta += [
            f"[<:myAnimeList:1073442204921643048> MyAnimeList](<https://myanimelist.net/manga/{m}>)"]
        pdta += [
            f"[<:shikimori:1073441855645155468> Шикимори](<https://shikimori.one/mangas/{m}>)"]

    if len(pdta) > 0:
        pdta = ", ".join(pdta)
        pdta = "\n**External Sites**\n" + pdta
    else:
        pdta = ""

    # get the genres
    tgs = []
    cw = False
    syChkMark = ''
    for g in alm['genres']:
        tgs += [f"{g}"]
    for t in alm['tags']:
        if t['name'] not in bannedTags:
            # check if tag is spoiler
            if t['isMediaSpoiler'] is True:
                tgs += [f"||{t['name']}||"]
            else:
                tgs += [f"{t['name']}"]
        elif (t['name'] in bannedTags) and (isNsfw is True):
            if t['isMediaSpoiler'] is True:
                tgs += [f"||{t['name']} **!**||"]
            else:
                tgs += [f"{t['name']} **!** "]
            cw = True
        else:
            syChkMark = '*'

    if (len(tgs) is None) or (len(tgs) == 0):
        tgs = "*None*"
    elif len(tgs) > 20:
        tgss = sorted(set(tgs[:20]), key=str.casefold)
        tgs = ", ".join(tgss)
        tgs += f", *and {len(tgss) - 20} more*"
    else:
        tgss = sorted(set(tgs), key=str.casefold)
        tgs = ", ".join(tgss)

    stat = str(alm['status'])
    # Only capitalize the first letter, rest must lowercase
    stat = stat[0].upper() + stat[1:].lower()

    # Set start date
    stadd = alm['startDate']
    std = stadd['day']
    stm = stadd['month']
    sty = stadd['year']
    daten = datetime.datetime(1970, 1, 1)
    daten = daten.replace(tzinfo=datetime.timezone.utc)
    if (std is None) and (stm is None) and (sty is None):
        ast = "Unknown date"
    else:
        if std is None:
            std = 1
        if stm is None:
            stm = 1
        if sty is None:
            sty = 1970
        ast = (datetime.datetime.strptime(
            f'{sty}-{stm}-{std}T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z') - daten).total_seconds()
        ast = str(ast).removesuffix('.0')
        ast = "<t:" + ast + ":D>"

    # Set end date
    enddd = alm['endDate']
    edd = enddd['day']
    edm = enddd['month']
    edy = enddd['year']
    daten = datetime.datetime(1970, 1, 1)
    daten = daten.replace(tzinfo=datetime.timezone.utc)
    if stat == 'Releasing':
        aen = "Ongoing"
    elif stat == 'Finished':
        if edd is None:
            edd = 1
        if edm is None:
            edm = 1
        if edy is None:
            edy = 1970
        aen = (datetime.datetime.strptime(
            f'{edy}-{edm}-{edd}T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z') - daten).total_seconds()
        aen = str(aen).removesuffix('.0')
        aen = "<t:" + aen + ":D>"
    else:
        aen = ast

    vols = alm['volumes']
    if vols is None:
        vols = "*??*"
    chps = alm['chapters']
    if chps is None:
        chps = "*??*"

    if (enChkMark != '') or (syChkMark != ''):
        chkMsg = "\n* Data might be inaccurate due to bot rules/config, please check source for more information."
    else:
        chkMsg = ""

    if cw is True:
        cw = "\n* Some tags marked with \"!\" are NSFW."
    else:
        cw = ""

    embed = interactions.Embed(
        author=interactions.EmbedAuthor(
            name="AniList Manga",
            url="https://anilist.co",
            icon_url="https://anilist.co/img/icons/android-chrome-192x192.png"
        ),
        title=rot,
        url=f"https://anilist.co/manga/{id}",
        description=f"""*`{id}`, {form}, {year}, ⭐ {scr}/100, by {pvd}*

> {cyno}
{pdta}
""",
        color=0x2E51A2,
        thumbnail=interactions.EmbedImageStruct(
            url=poster
        ),
        fields=[
            interactions.EmbedField(
                name=f"English Title{enChkMark}",
                value=ent,
                inline=True
            ),
            interactions.EmbedField(
                name="Native Title",
                value=nat,
                inline=True
            ),
            interactions.EmbedField(
                name="Synonyms",
                value=syns
            ),
            interactions.EmbedField(
                name=f"Genres and Tags{syChkMark}",
                value=tgs
            ),
            interactions.EmbedField(
                name="Volumes",
                value=vols,
                inline=True
            ),
            interactions.EmbedField(
                name="Chapters",
                value=chps,
                inline=True
            ),
            interactions.EmbedField(
                name="Status",
                value=stat,
                inline=True
            ),
            interactions.EmbedField(
                name="Published",
                value=f"""{ast} - {aen} ({ast.replace("D", "R")})"""
            )
        ],
        image=interactions.EmbedImageStruct(
            url=background
        ),
        footer=interactions.EmbedFooter(
            text=f"{chkMsg}{cw}"
        )
    )

    return embed

    # return msg.strip()


async def bypassAniListEcchiTag(alm: dict) -> bool:
    """Bypass 'NSFW' tagged entry on AniList if it's only an ecchi tag"""
    # get the genres
    tgs = []
    for g in alm['genres']:
        tgs += [f"{g}"]
    for t in alm['tags']:
        tgs += [f"{t['name']}"]

    if "Ecchi" in tgs:
        return True
    else:
        return False

