from modules.commons import *
from modules.const import *
from modules.tmdb import *


async def searchSimklId(title_id: str, platform: str, media_type: str = None) -> int:
    """Search SIMKL title ID  from other platforms"""
    url = f'https://api.simkl.com/search/id/?{platform}={title_id}'
    if media_type is not None:
        url += f'&type={media_type}'
    url += f"&client_id={SIMKL_CLIENT_ID}"
    try:
        async with aiohttp.ClientSession() as sSession:
            async with sSession.get(url) as sResp:
                idFound = await sResp.json()
                fin = idFound[0]['ids']['simkl']
            await sSession.close()
            return fin
    except:
        return 0


async def getSimklID(simkl_id: int, media_type: str) -> dict:
    """Get external IDs provided by SIMKL"""
    try:
        if simkl_id == 0:
            raise Exception('Simkl ID is 0')
        else:
            async with aiohttp.ClientSession() as gSession:
                async with gSession.get(f'https://api.simkl.com/{media_type}/{simkl_id}?client_id={SIMKL_CLIENT_ID}&extended=full') as gResp:
                    animeFound = await gResp.json()
                    data = animeFound['ids']
                    # Null safe result, if any of the key is not found, it will be replaced with None
                    data = {
                        "title": animeFound.get('title', None),
                        "simkl": data.get('simkl', None),
                        "slug": data.get('slug', None),
                        "poster": animeFound.get('poster', None),
                        "fanart": animeFound.get('fanart', None),
                        "aniType": animeFound.get('anime_type', None),
                        "type": animeFound.get('type', None),
                        "allcin": data.get('allcin', None),
                        "anfo": data.get('anfo', None),
                        "ann": data.get('ann', None),
                        "imdb": data.get('imdb', None),
                        "mal": data.get('mal', None),
                        "offjp": data.get('offjp', None),
                        "tmdb": data.get('tmdb', None),
                        "tvdb": data.get('tvdb', None),
                        "tvdbslug": data.get('tvdbslug', None),
                        "wikien": data.get('wikien', None),
                        "wikijp": data.get('wikijp', None),
                    }
                await gSession.close()
                return data
    except:
        return simkl0rels


async def searchSimkl(query: str, mediaType: str = 'tv') -> dict:
    """Search TV/Movie on SIMKL"""
    query = urlparse.quote(query)
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.simkl.com/search/{mediaType}?q={query}&client_id={SIMKL_CLIENT_ID}&page=1&limit=5') as resp:
            if resp.status != 200:
                raise Exception(f"SIMKL API returned {resp.status}")
            simklRes = await resp.json()
        await session.close()
        if len(simklRes) == 0:
            raise Exception('**No results found!**')
        return simklRes


async def getSimklData(id: int, mediaType: str = 'tv') -> dict:
    """Get information of a title in SIMKL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.simkl.com/{mediaType}/{id}?client_id={SIMKL_CLIENT_ID}&extended=full') as resp:
            if resp.status != 200:
                raise Exception(f"SIMKL API returned {resp.status}")
            simklRes = await resp.json()
        await session.close()
        return simklRes


async def generateSimkl(data: dict, mediaType: str = "tv", isNsfw: bool = False, mediaNsfw: bool = False) -> interactions.Embed:
    """Generate embed from SIMKL data"""
    if isNsfw is None:
        msgForThread = warnThreadCW
    else:
        msgForThread = ''

    if isNsfw is False and mediaNsfw is True:
        raise Exception(
            f'{EMOJI_FORBIDDEN} **NSFW content is not allowed!**\nOnly NSFW channels are allowed to search NSFW content.{msgForThread}')

    id = data['ids']['simkl']
    ent = data['title']
    syns = data.get('alt_titles', None)
    if syns is not None:
        syns = [x['name'] for x in syns if x['name'] != ent]
        syns = sorted(set(syns), key=str.casefold)
        synsl = len(syns)

        if synsl > 8:
            syns = syns[:8]
            syns = ", ".join(syns) + f" and {synsl - 8} more"
        elif synsl > 1:
            syns = ", ".join(syns)
        elif synsl == 1:
            syns = syns[0]
    else:
        syns = "*None*"

    network = data.get('network', None)
    cert = data['certification']

    eps = data.get('total_episodes', None)
    if eps in ['', None, 0]:
        eps = "*??*"

    runtime = data.get('runtime', None)
    if runtime in ['', None, 0]:
        runtime = ""
    else:
        runtime = " (" + str(runtime) + " mins/ep)" if mediaType == 'tv' else str(runtime) + " mins"

    country = data.get('country', None)
    if country in ['', None]:
        country = "*Unknown*"
    else:
        country = country.upper()

    stat = data.get('status', None)
    if stat == 'tba':
        stat = ', To Be Announced'
    elif stat is not None:
        stat = ", " + stat.title()
    else:
        stat = ''

    rate = data.get('ratings', None)
    if rate not in ['', None, 0]:
        scr = data['ratings']['simkl']['rating']
        if scr in ['', None, 0]:
            scr = "0"

        pvd = data['ratings']['simkl']['votes']
        if pvd in ['', None, 0]:
            pvd = "0 person voted"
        elif pvd == 1:
            pvd = "1 person voted"
        else:
            pvd = f"{pvd:,} people voted"
    else:
        scr = "0"
        pvd = "0 person voted"

    # "first_aired":"2019-11-01T04:00:00Z"
    if mediaType == 'tv':
        astn = data.get('first_aired', None)
        if astn in ['', None]:
            ast = "TBA"
            tsa = ""
            passing = None
        else:
            ast = datetime.datetime.strptime(astn, '%Y-%m-%dT%H:%M:%S%z')
            tsa = "(<t:" + str(int(ast.timestamp())) + ":R>)"
            passing = ast
            ast = "<t:" + str(int(ast.timestamp())) + ":D>"
    elif mediaType == 'movies':
        astn = data.get('released', None)
        if astn in ['', None]:
            ast = "TBA"
            tsa = ""
            passing = None
        else:
            astn += "T00:00:00+00:00"
            ast = datetime.datetime.strptime(astn, '%Y-%m-%dT%H:%M:%S%z')
            tsa = "(<t:" + str(int(ast.timestamp())) + ":R>)"
            passing = ast
            ast = "<t:" + str(int(ast.timestamp())) + ":D>"

    year = data.get('year', None)

    if eps != "*??*" and passing is not None and stat == ", Ended":
        # roughly calculate the end date by determining the number of episodes released
        # per week and then adding that to the first aired date
        # this is not accurate but it's better than nothing
        aen = passing + datetime.timedelta(weeks=eps)
        aen = "<t:" + str(int(aen.timestamp())) + ":D>"
    elif stat == ", Airing":
        aen = "TBA"
    elif stat == ", To Be Announced":
        aen = "TBA"
    else:
        aen = "*Unknown*"

    if tsa not in ['', None]:
        tsa = " " + tsa
    else:
        tsa = ""

    if mediaType == 'tv':
        if ast == "TBA" and aen == "TBA":
            date = "TBA"
        else:
            date = f"{ast} - {aen}{tsa}"
    elif mediaType == 'movies':
        date = f"{ast}{tsa}"

    cyno = data.get('overview', None)
    if cyno in [None, '']:
        cyno = "*No description provided*"
    else:
        cyno = cyno.replace("\r", "")
        cyno = cyno.split('\n')
        cynl = len(cyno)
        cynoin = cyno[0]
        cynmo = f"\n> \n> [Read more on SIMKL](https://simkl.com/{mediaType}/{id})"

        if len(str(cynoin)) <= 150:
            daff = cynoin
            if cynl >= 2:
                for i in range(2, cynl + 1):
                    if (len(str(cyno[i])) > 0) or (cyno[i] != ""):
                        cynoAdd = cyno[i]
                        cynoAdd = sanitizeMarkdown(cynoAdd)
                        break
                cyno = sanitizeMarkdown(daff)
                cyno += '\n> \n> '
                cyno += trimCyno(cynoAdd)
            else:
                cyno = sanitizeMarkdown(daff)
        elif len(str(cynoin)) >= 1000:
            cyno = trimCyno(cynoin)
        else:
            cyno = cynoin

        if (cyno[-3:] == "...") or ((len(str(cynoin)) >= 150) and (cynl > 3)) or ((len(str(cynoin)) >= 1000) and (cynl > 1)):
            cyno += cynmo

    tgs = data.get('genres', None)
    if (len(tgs) == 0) or tgs is None:
        tgs = "*None*"
    elif len(tgs) > 20:
        tgss = sorted(set(tgs[:20]), key=str.casefold)
        tgs = ', '.join(tgss)
        tgs += f", and {len(tgs) - 20} more"
    else:
        tgss = sorted(set(tgs), key=str.casefold)
        tgs = ', '.join(tgss)

    poster = data.get('poster', None)
    fanart = data.get('fanart', None)

    if poster is not None:
        poster = interactions.EmbedImageStruct(
            url=f"https://simkl.in/posters/{poster}_m.webp"
        )
    else:
        poster = None
    if fanart is not None:
        fanart = interactions.EmbedImageStruct(
            url=f"https://simkl.in/fanart/{fanart}_w.webp"
        )
    else:
        fanart = None

    finfields = [
        interactions.EmbedField(
            name="Synonyms",
            value=syns,
            inline=False
        ),
        interactions.EmbedField(
            name="Genres",
            value=tgs,
            inline=False
        ),
    ]
    if mediaType == 'tv':
        finfields.append(
            interactions.EmbedField(
                name="Network",
                value=network if network is not None else "*None*",
                inline=True
            )
        )
    finfields += [
        interactions.EmbedField(
            name="Certification",
            value=cert if cert is not None else "*None*",
            inline=True
        ),
        interactions.EmbedField(
            name="Country",
            value=country,
            inline=True
        ),
        interactions.EmbedField(
            name="Episodes and Duration" if mediaType == 'tv' else "Duration",
            value=f"{eps}{runtime}" if mediaType == 'tv' else f"{runtime}",
            inline=True
        ),
        interactions.EmbedField(
            name=f"Airing Date" if mediaType == 'tv' else "Release Date",
            value=date,
            inline=True
        )
    ]

    embed = interactions.Embed(
        author=interactions.EmbedAuthor(
            name=f"SIMKL {'TV' if mediaType == 'tv' else 'Movie'}",
            url=f"https://simkl.com",
            icon_url="https://media.discordapp.net/attachments/1078005713349115964/1094570318967865424/ico_square_1536x1536.png"
        ),
        title=ent,
        url=f"https://simkl.com/{mediaType}/{id}",
        description=f"""*`{id}`, {mediaType.title()}{stat}, {year}, ⭐ {scr}/10 by {pvd}*

> {cyno}""",
        color=0x0B0F10,
        fields=finfields,
        image=fanart,
        thumbnail=poster
    )

    return embed


async def simklSubmit(ctx, simkl_id, media: str = 'tv'):
    trailer = None
    try:
        data: dict = await getSimklData(id=simkl_id, mediaType=media)
        nsfw_bool = await getNsfwStatus(channel=ctx.channel)
        try:
            tmdbNsfw = await tmdb_getNsfwStatus(id=data['ids']['tmdb_id'], mediaType=media)
        except KeyError:
            tmdbNsfw = False
        dcEm = await generateSimkl(data=data, mediaType=media, isNsfw=nsfw_bool, mediaNsfw=tmdbNsfw)
        if data.get('trailers', None) is not None:
            try:
                trailer = generateTrailer(data=data['trailers'][0], isSimkl=True)
            except KeyError:
                trailer = None
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))

    await ctx.send(embeds=dcEm, components=trailer)
