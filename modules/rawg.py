from modules.commons import *
from modules.const import *


async def searchRawg(query: str) -> dict:
    """Search game on RAWG"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={query}&page_size=5') as resp:
            if resp.status != 200:
                raise Exception(f"RAWG API returned {resp.status}")
            rawgRes = await resp.json()
        await session.close()
        return rawgRes['results']


async def getRawgData(slug: str) -> dict:
    """Get information of a title in RAWG"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.rawg.io/api/games/{slug}?key={RAWG_API_KEY}') as resp:
            if resp.status != 200:
                raise Exception(f"RAWG API returned {resp.status}")
            rawgRes = await resp.json()
        await session.close()
        if len(rawgRes) == 0:
            raise Exception("**No results found!**")
        return rawgRes


async def generateRawg(data: dict) -> interactions.Embed:
    """Generate embed for RAWG API"""
    # get the data
    id = data['slug']
    syns = data['alternative_names']
    ent = data['name']
    nat = data['name_original']
    ogt = [ent, nat]
    syns = [x for x in syns if x not in ogt]
    syns = sorted(set(syns), key=str.casefold)
    synsl = len(syns)

    if synsl > 8:
        syns = syns[:8]
        syns = ", ".join(syns)
        syns += f", *and {synsl - 8} more*"
    elif synsl > 0:
        syns = ", ".join(syns)
    else:
        syns = "*None*"

    pfs = []
    for pf in data['platforms']:
        pfs += [f"{pf['platform']['name']}"]

    pfs = sorted(set(pfs), key=str.casefold)
    pfs = ", ".join(pfs)

    scr = data['rating']
    mc_scr = data['metacritic']

    rte = data['esrb_rating']
    if rte is None:
        rte = "Unknown Rating"
    else:
        rte = rte['name']

    devs = []
    for d in data['developers']:
        devs += [f"{d['name']}"]

    if len(devs) > 0:
        devs = sorted(set(devs), key=str.casefold)
        devs = ", ".join(devs)
    else:
        devs = "*None*"

    pubs = []
    for p in data['publishers']:
        pubs += [f"{p['name']}"]

    if len(pubs) > 0:
        pubs = sorted(set(pubs), key=str.casefold)
        pubs = ", ".join(pubs)
    else:
        pubs = "*None*"

    cyno = data['description_raw']
    if cyno is None:
        cyno = "*No description provided*"
    else:
        cyno = cyno.replace("\r", "")
        cyno = cyno.split('\n')
        cynl = len(cyno)
        cynoin = cyno[0]
        cynmo = f"\n> \n> [Read more on RAWG](https://rawg.io/games/{id})"

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

    tgs = []
    for g in data['genres']:
        tgs += [f"{g['name']}"]
    for t in data['tags']:
        tgs += [f"{t['name']}"]

    if len(tgs) > 20:
        lefties = int(len(tgs) - int(20))
        tgs = sorted(set(tgs[:20]), key=str.casefold)
        tgs = ", ".join(tgs)
        tgs += f", *and {lefties} more*"
    elif len(tgs) > 0:
        tgs = sorted(set(tgs), key=str.casefold)
        tgs = ", ".join(tgs)
    else:
        tgs = "*None*"

    daten = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

    if data['tba'] is False:
        rel = data['released']
        rel = re.sub(r'^(\d{4})-(\d{2})-(\d{2})', r'\1-\2-\3', rel)
        rel = (datetime.datetime.strptime(
            f"{rel}+0000", "%Y-%m-%d%z") - daten).total_seconds()
        # reconvert from Epoch to year
        year = datetime.datetime.utcfromtimestamp(rel).strftime('%Y')
        rel = f"<t:{int(rel)}:D> (<t:{int(rel)}:R>)"
    else:
        rel = "*TBA*"
        year = "Unknown year"

    pdt = []
    web = data['website']
    if web != "":
        pdt += [{'name': 'Website', 'value': f"{data['website']}"}]
    mc_url = data['metacritic_url']
    if mc_url != "":
        pdt += [{'name': 'Metacritic', 'value': f"{data['metacritic_url']}"}]
    reddit = data['reddit_url']
    if reddit != "":
        if re.match(r'^http(s)?://(www.)?reddit.com/r/(\w+)', reddit):
            subreddit = reddit
        elif re.match(r'r/(\w+)', reddit):
            subreddit = f"https://reddit.com/{reddit}"
        elif re.match(r'^(\w+)', reddit):
            subreddit = f"https://reddit.com/r/{reddit}"
        pdt += [{'name': 'Reddit', 'value': f"{subreddit}"}]

    if len(pdt) > 0:
        pdta = []
        for p in pdt:
            pdta += [f"[{p['name']}](<{p['value']}>)"]
        pdta = ", ".join(pdta)
        pdta = "\n**External Sites**\n" + pdta
    else:
        pdta = ""

    bg = data['background_image']

    embed = interactions.Embed(
        author=interactions.EmbedAuthor(
            name="RAWG Game",
            url=f"https://rawg.io/",
            icon_url="https://pbs.twimg.com/profile_images/951372339199045632/-JTt60iX_400x400.jpg"
        ),
        title=ent,
        url=f"https://rawg.io/games/{id}",
        description=f"""*{rte}, {year}, ⭐ {scr}/5 (Metacritic: {mc_scr})*

> {cyno}
{pdta}
""",
        color=0x1F1F1F,
        fields=[
            interactions.EmbedField(
                name="English Title",
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
                value=syns,
                inline=False
            ),
            interactions.EmbedField(
                name="Genres and Tags",
                value=tgs,
                inline=False
            ),
            interactions.EmbedField(
                name="Platforms",
                value=pfs,
                inline=False
            ),
            interactions.EmbedField(
                name="Developers",
                value=devs,
                inline=True
            ),
            interactions.EmbedField(
                name="Publishers",
                value=pubs,
                inline=True
            ),
            interactions.EmbedField(
                name="Release Date",
                value=rel,
                inline=True
            ),
        ],
        image=interactions.EmbedImageStruct(
            url=bg
        )
    )
    return embed


async def rawgSubmit(ctx, slug: str):
    try:
        gameData = await getRawgData(slug=slug)
        dcEm = await generateRawg(data=gameData)
    except Exception as e:
        dcEm = exceptionsToEmbed(returnException(e))

    await ctx.send("", embeds=dcEm)
