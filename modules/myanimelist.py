from modules.simkl import *
from modules.commons import *
from modules.kitsu import *

async def checkClubMembership(username) -> dict:
    """Check if user is a member of any club"""
    jikanUser = await jikan.users(username=f'{username}', extension='clubs')
    return jikanUser['data']

def definejikanException(errmsg: str) -> interactions.Embed:
    """Define what HTTP error AioJikan/Jikan/MyAnimeList threw"""
    e = str(errmsg).split('=')
    print(e)
    try:
        etype = int(str(e[1]).split(',')[0])
        errm = e[3].strip()
        if len(e) >= 4:
            for i in range(4, len(e)):
                errm += f"={e[i]}"
        if etype == 403:
            em = f"**Jikan unable to reach MyAnimeList at the moment.**\nPlease try again in 3 seconds."
        elif etype == 404:
            em = f"**I couldn't find the user on MAL.**\nCheck the spelling or well, maybe they don't exist? 🤔"
        elif etype == 408:
            em = f"**Jikan had a timeout while fetching your data**\nPlease try again in 3 seconds."
        else:
            em = f"HTTP {etype}\n{errm}"
    except IndexError:
        em = "Unknown error."
    return em

async def getJikanUserData(uname) -> dict:
    """Get user data from Jikan"""
    try:
        jikanData = await jikan.users(username=f'{uname}')
        jikanData = jikanData['data']
        return jikanData
    except Exception as e:
        raise Exception(e)


async def searchJikanAnime(title: str) -> dict:
    """Search anime on MyAnimeList via Jikan (inaccurate)"""
    jikanParam = {
        'limit': '10'
    }
    try:
        jikanData = await jikan.search('anime', f'{title}', parameters=jikanParam)
        jikanData = jikanData['data']
        return jikanData
    except Exception as e:
        raise Exception(e)


async def getJikanAnime(mal_id: int) -> dict:
    """Get anime data from MyAnimeList via Jikan"""
    id = mal_id
    try:
        jikanData = await jikan.anime(id)
        jikanData = jikanData['data']
        return jikanData
    except Exception as e:
        raise Exception(e)

def lookupRandomAnime() -> int:
    """Lookup random anime from MAL"""
    seed = getRandom()
    # open database/mal.csv
    df = pd.read_csv("database/mal.csv", sep="\t")
    # get random anime
    randomAnime = df.sample(n=1, random_state=seed)
    # get anime id
    randomAnimeId: int = randomAnime['mal_id'].values[0]
    return randomAnimeId


async def generateMal(entry_id: int, isNsfw: bool = False, alDict: dict = None, animeApi: dict = None) -> interactions.Embed:
    """Generate an embed for /anime with MAL via Jikan"""
    j = await getJikanAnime(entry_id)
    if alDict is not None:
        al = alDict[0]
    else:
        al = None
    if isNsfw is None:
        msgForThread = warnThreadCW
    else:
        msgForThread = ''
    if isNsfw is not True:
        for g in j['genres']:
            gn = g['name']
            if "Hentai" in gn:
                raise Exception(
                    f'{EMOJI_FORBIDDEN} **NSFW is not allowed!**\nOnly NSFW channels are allowed to search NSFW content.{msgForThread}')

    m = j['mal_id']

    if j['synopsis'] is not None:
        # remove \n\n[Written by MAL Rewrite]
        jdata = j['synopsis'].replace("\n\n[Written by MAL Rewrite]", "")
        # try to decode ampersands
        jdata = html.unescape(jdata)
        j_spl = jdata.split("\n")
        synl = len(j_spl)
        cynoin = j_spl[0]

        cynmo = f"\n> \n> Read more on [MyAnimeList](<https://myanimelist.net/anime/{m}>)"

        if len(str(cynoin)) <= 150:
            cyno = cynoin
            if synl >= 3:
                cyno += "\n> \n> "
                cyno += trimCyno(j_spl[2])
        elif len(str(cynoin)) >= 1000:
            cyno = trimCyno(cynoin)
            # when cyno has ... at the end, it means it's trimmed, then add read more
        else:
            cyno = cynoin

        if (cyno[-3:] == "...") or ((len(str(cynoin)) >= 150) and (synl > 3)) or ((len(str(cynoin)) >= 1000) and (synsl > 1)):
            cyno += cynmo

    else:
        cyno = "*None*"

    jJpg = j['images']['jpg']
    note = "Images from "

    if al is None:
        al = {
            'bannerImage': None,
            'coverImage': {
                'extraLarge': None
            }
        }

    alPost = al['coverImage']['extraLarge']
    alBg = al['bannerImage']

    smId = await searchSimklId(m, 'mal')
    smk = await getSimklID(smId, 'anime')
    smkPost = smk.get('poster', None)
    smkBg = smk.get('fanart', None)
    smkPost = f"https://simkl.in/posters/{smkPost}_m.webp" if smkPost is not None else None
    smkBg = f"https://simkl.in/fanart/{smkBg}_w.webp" if smkBg is not None else None

    if (animeApi['kitsu'] is not None) and (((alPost is None) and (alBg is None)) or ((smkPost is None) and (smkBg is None))):
        kts = await getKitsuMetadata(animeApi['kitsu'], 'anime')
    else:
        kts = {
            "data": {
                "attributes": {
                    "posterImage": None,
                    "coverImage": None
                }
            }
        }

    ktsPost = kts['data']['attributes'].get('posterImage', None)
    ktsPost = ktsPost.get('original', None) if ktsPost is not None else None
    ktsBg = kts['data']['attributes'].get('coverImage', None)
    ktsBg = ktsBg.get('original', None) if ktsBg is not None else None

    malPost = jJpg['large_image_url'] if jJpg['large_image_url'] is not None else j['image_url']
    malBg = ""

    poster = alPost if alPost is not None else smkPost if smkPost is not None else ktsPost if ktsPost is not None else malPost
    postNote = "AniList" if alPost is not None else "SIMKL" if smkPost is not None else "Kitsu" if ktsPost is not None else "MyAnimeList"
    background = alBg if alBg is not None else smkBg if smkBg is not None else ktsBg if ktsBg is not None else malBg
    bgNote = "AniList" if alBg is not None else "SIMKL" if smkBg is not None else "Kitsu" if ktsBg is not None else "MyAnimeList"

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
    for g in j["genres"]:
        gn = g["name"]
        tgs += [f"{gn}"]
    for g in j["themes"]:
        gn = g["name"]
        tgs += [f"{gn}"]
    for g in j["demographics"]:
        gn = g["name"]
        tgs += [f"{gn}"]

    if len(tgs) is None:
        tgs = "*None*"
    elif len(tgs) > 0:
        tgs = sorted(set(tgs), key=str.casefold)
        tgs = ", ".join(tgs)
    else:
        tgs = "*None*"
    year = j['aired']['prop']['from']['year']
    if (year == 0) or (year is None):
        year = 'year?'
    astn = j['aired']['from']
    aenn = j['aired']['to']
    astr = j['aired']['string']
    ssonn = j['season']
    daten = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    bcast = j['broadcast']

    # Grab studio names on j['studios'][n]['name']
    stdio = []
    for s in j['studios']:
        stdio += [s['name']]
    if len(stdio) > 0:
        stdio = ", ".join(stdio)
    else:
        stdio = "*None*"

    # start date logic
    if astn is not None:
        # Check if title is airing/aired or TBA by checking astr in regex
        if re.match(r'^([\d]{4})', astr) or re.match(r'^([a-zA-Z]{3} [\d]{4})', astr):
            ast = astr.split(" to ")[0]
            tsa = ""
        elif re.match(r'^([a-zA-Z]{3} [\d]{1,2}, [\d]{4})', astr):
            if (bcast['string'] == "Unknown") or (bcast['string'] is None) or (bcast['time'] is None):
                astn = astn.replace('+00:00', '+0000')
                ast = (datetime.datetime.strptime(
                    astn, '%Y-%m-%dT%H:%M:%S%z') - daten).total_seconds()
            else:
                # Split bcast.time into hours and minutes
                bct = bcast['time'].split(":")
                prop = j['aired']['prop']['from']
                # Convert bct to datetime
                ast = (datetime.datetime(prop['year'], prop['month'], prop['day'], int(
                    bct[0]), int(bct[1]), tzinfo=ZoneInfo(bcast['timezone'])) - daten).total_seconds()
            ast = str(ast).removesuffix('.0')
            tsa = "(<t:" + ast + ":R>)"
            ast = "<t:" + ast + ":D>"
    else:
        ast = "TBA"
        tsa = ""

    # end date logic
    if aenn is not None:
        if re.match(r'^([a-zA-Z]{3} [\d]{1,2}, [\d]{4})', astr):
            if (bcast['string'] == "Unknown") or (bcast['string'] is None) or (bcast['time'] is None):
                aenn = aenn.replace('+00:00', '+0000')
                aen = (datetime.datetime.strptime(
                    aenn, '%Y-%m-%dT%H:%M:%S%z') - daten).total_seconds()
            else:
                # Split bcast.time into hours and minutes
                bct = bcast['time'].split(":")
                prop = j['aired']['prop']['to']
                # Convert bct to datetime
                aen = (datetime.datetime(prop['year'], prop['month'], prop['day'], int(
                    bct[0]), int(bct[1]), tzinfo=ZoneInfo(bcast['timezone'])) - daten).total_seconds()
            aen = str(aen).removesuffix('.0')
            aen = "<t:" + aen + ":D>"
        elif re.match(r'^([a-zA-Z]{3} [\d]{4})', astr):
            aen = astr.split(" to ")[1]
    elif j['status'] == 'Currently Airing':
        aen = "Ongoing"
    elif (j['status'] == 'Not yet aired') or (astr == 'Not available'):
        aen = "TBA"
    else:
        aen = ast

    # Build date
    if tsa is not None:
        tsa = " " + tsa
    else:
        tsa = ""

    if (ast == "TBA") and (aen == "TBA"):
        date = "TBA"
    else:
        date = f"{ast} - {aen} {tsa}"

    if ssonn is not None:
        sson = str(ssonn).capitalize()
    elif re.match("^[0-9]{4}$", ast):
        sson = "Unknown"
    elif j['aired']['prop']['from']['month'] is not None:
        astn = astn.replace("+00:00", "+0000")
        astn = datetime.datetime.strptime(
            astn, '%Y-%m-%dT%H:%M:%S%z')
        sson = astn.strftime('%m')
        if sson in ['01', '02', '03']:
            sson = 'Winter'
        elif sson in ['04', '05', '06']:
            sson = 'Spring'
        elif sson in ['07', '08', '09']:
            sson = 'Summer'
        elif sson in ['10', '11', '12']:
            sson = 'Fall'
    else:
        sson = "Unknown"

    rot = j['title']

    nat = j['title_japanese']
    if (nat == '') or (nat is None):
        nat = "*None*"

    ent = j['title_english']
    # create a synonyms list
    syns = []
    for s in j['titles']:
        if s['type'] not in ['Default', 'English']:
            syns += [s['title']]
    if (ent is None) or (ent == ''):
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
        chkMsg = "\n* Data might be inaccurate due to bot rules/config, please check source for more information."
    else:
        enChkMark = ''
        chkMsg = ""

    note += chkMsg

    ogt = [rot, nat, ent]
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
    elif synsl == 0:
        syns = "*None*"

    # format people voted for to be more readable (1,000 instead of 1000)
    pvd = j['scored_by']
    if pvd is None:
        pvd = "0 person voted"
    elif pvd > 1:
        pvd = f"{pvd:,} people voted"
    elif pvd == 1:
        pvd = f"1 person voted"

    eps = j['episodes']
    if (eps == 0) or (eps is None):
        eps = '*??*'

    stat = j['status']
    if (stat == '') or (stat is None):
        stat = "*Unknown*"

    dur = j['duration']
    if (dur == '') or (dur is None):
        dur = "*Unknown*"

    scr = j['score']
    if (scr == '') or (scr is None):
        scr = "0"

    embed = interactions.Embed(
        author=interactions.EmbedAuthor(
            name="MyAnimeList Anime",
            url="https://myanimelist.net",
            icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
        ),
        title=rot,
        url=f"https://myanimelist.net/anime/{m}",
        description=f"""*`{m}`, {j['type']}, {sson} {year}, ⭐ {scr}/10 by {pvd}*

> {cyno}

*Use `/anime relations id:{m} platform:MyAnimeList` to see external links!*
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
                name="Genres and Themes",
                value=tgs
            ),
            interactions.EmbedField(
                name="Eps/Duration",
                value=f"{eps} ({dur})",
                inline=True
            ),
            interactions.EmbedField(
                name="Status",
                value=stat,
                inline=True
            ),
            interactions.EmbedField(
                name="Studio",
                value=stdio,
                inline=True
            ),
            interactions.EmbedField(
                name="Aired",
                value=date
            )
        ],
        image=interactions.EmbedImageStruct(
            url=background
        ),
        footer=interactions.EmbedFooter(
            text=note
        )
    )

    return embed


def generateProfile(malProfile: dict, extend: bool = False) -> interactions.Embed:
    """Generate embed for profile command"""
    mun = malProfile['username'].replace("_", "\\_")
    mid = malProfile['mal_id']
    ani = malProfile['statistics']['anime']
    man = malProfile['statistics']['manga']
    bth = None
    if malProfile['birthday'] is not None:
        bth = malProfile['birthday'].replace("+00:00", "+0000")
        bth = int(datetime.datetime.strptime(
            bth, "%Y-%m-%dT%H:%M:%S%z").timestamp())
    dtJoin = malProfile['joined'].replace("+00:00", "+0000")
    dtJoin = int(datetime.datetime.strptime(
        dtJoin, "%Y-%m-%dT%H:%M:%S%z").timestamp())
    bbd = ""
    if bth is not None:
        # convert bth from timestamp back to datetime
        bthRaw = datetime.datetime.fromtimestamp(int(bth))
        today = datetime.datetime.now(tz=datetime.timezone.utc)
        currYear = today.year
        upcoming = bthRaw.replace(year=currYear)
        if int(upcoming.timestamp()) < int(today.timestamp()):
            upcoming = upcoming.replace(year=currYear + 1)
        bbd = f"\nBirthday: <t:{int(bth)}:D> <t:{int(bth)}:R> (next birthday <t:{int(upcoming.timestamp())}:R>)"
    desc = f"[Anime List](https://myanimelist.net/animelist/{mun}) | [Manga List](https://myanimelist.net/mangalist/{mun})"
    fds = [
        interactions.EmbedField(
            name="Profile",
            value=f"""User ID: `{mid}`
Account created: <t:{dtJoin}:D> (<t:{dtJoin}:R>){bbd}""",
            inline=False
        )
    ]
    img = None
    foo = "Powered by MyAnimeList (via Jikan). Data may be inaccurate due to Jikan caching. To see more information, append \"extended: True\" argument!"
    if extend is True:
        desc += f"\nSee also on 3rd party sites: [MAL Badges](https://mal-badges.com/users/{mun}), [anime.plus malgraph](https://anime.plus/{mun})"
        fds += [
            interactions.EmbedField(
                name="Anime Stats",
                value=f"""• Days watched: {ani['days_watched']}
• Mean score: {ani['mean_score']}
• Total entries: {ani['total_entries']}
👀 {ani['watching']} | ✅ {ani['completed']} | ⏸️ {ani['on_hold']} | 🗑️ {ani['dropped']} | ⏰ {ani['plan_to_watch']}
*Episodes watched: {ani['episodes_watched']}*""",
                inline=True
            ),
            interactions.EmbedField(
                name="Manga Stats",
                value=f"""• "Days" read: {man['days_read']}
• Mean score: {man['mean_score']}
• Total entries: {man['total_entries']}
👀 {man['reading']} | ✅ {man['completed']} | ⏸️ {man['on_hold']} | 🗑️ {man['dropped']} | ⏰ {man['plan_to_read']}
*Chapters read: {man['chapters_read']}*
*Volumes read: {man['volumes_read']}*""",
                inline=True
            )
        ]
        img = interactions.EmbedImageStruct(
            url=f"https://malheatmap.com/users/{mun}/signature"
        )
        foo = "Powered by MyAnimeList (via Jikan) and MAL Heatmap. Data may be inaccurate due to Jikan caching."
    else:
        desc += f"\nTotal Anime: {ani['total_entries']} (⭐ {ani['mean_score']}) | Total Manga: {man['total_entries']} (⭐ {man['mean_score']})"

    if re.search(r"s$", mun):
        ttl = f"{mun}' MAL Profile"
    else:
        ttl = f"{mun}'s MAL Profile"

    embed = interactions.Embed(
        author=interactions.EmbedAuthor(
            name="MyAnimeList Profile",
            url="https://myanimelist.net",
            icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
        ),
        title=ttl,
        url=f"https://myanimelist.net/profile/{mun}",
        description=desc,
        thumbnail=interactions.EmbedImageStruct(
            url=f"https://cdn.myanimelist.net/images/userimages/{mid}.jpg"
        ),
        color=0x2E51A2,
        fields=fds,
        image=img,
        footer=interactions.EmbedFooter(
            text=foo
        )
    )
    return embed
