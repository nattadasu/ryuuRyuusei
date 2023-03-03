#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cspell:disable

import csv
import datetime
import json
import os
import time
from json import loads as jload
from zoneinfo import ZoneInfo

import aiohttp
import interactions
import pandas as pd
import regex as re
from dotenv import load_dotenv
from jikanpy import AioJikan

load_dotenv()

AUTHOR_USERID = os.getenv('AUTHOR_USERID')
AUTHOR_USERNAME = os.getenv('AUTHOR_USERNAME')
BOT_CLIENT_ID = os.getenv('BOT_CLIENT_ID')
BOT_SUPPORT_SERVER = os.getenv('BOT_SUPPORT_SERVER')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CLUB_ID = os.getenv('CLUB_ID')
SIMKL_CLIENT_ID = os.getenv('SIMKL_CLIENT_ID')
TRAKT_CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
VERIFICATION_SERVER = os.getenv('VERIFICATION_SERVER')
VERIFIED_ROLE = os.getenv('VERIFIED_ROLE')
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')

EMOJI_ATTENTIVE = os.getenv('EMOJI_ATTENTIVE')
EMOJI_DOUBTING = os.getenv('EMOJI_DOUBTING')
EMOJI_FORBIDDEN = os.getenv('EMOJI_FORBIDDEN')
EMOJI_SUCCESS = os.getenv('EMOJI_SUCCESS')
EMOJI_UNEXPECTED_ERROR = os.getenv('EMOJI_UNEXPECTED_ERROR')
EMOJI_USER_ERROR = os.getenv('EMOJI_USER_ERROR')

warnThreadCW = f"""

If you invoked this command outside (public or private) forum thread channel or regular text channel and **Age Restriction** is enabled, please contact developer of this bot as the feature only tested in forum thread and text channel.

You can simply access it on `/support`"""

bannedTags = [
    'Amputation', 'Anal Sex', 'Ashikoki', 'Asphyxiation',
    'Blackmail', 'Bondage', 'Boobjob', 'Cumflation',
    'Cunnilingus', 'Deepthroat', 'DILF', 'Fellatio',
    'Femdom', 'Futanari', 'Group Sex', 'Handjob',
    'Human Pet', 'Incest', 'Inseki', 'Irrumatio',
    'Lactation', 'Masochism', 'Masturbation', 'MILF',
    'Nakadashi', 'Pregnant', 'Prostitution', 'Public Sex',
    'Rape', 'Rimjob', 'Sadism', 'Scat',
    'Scissoring', 'Sex Toys', 'Squirting', 'Sumata',
    'Sweat', 'Tentacles', 'Threesome', 'Vore',
    'Voyeur', 'Watersports', 'Omegaverse'
]


bot = interactions.Client(
    token=BOT_TOKEN,
    presence=interactions.ClientPresence(
        since=None,
        activities=[
            interactions.PresenceActivity(
                name="Kagamine Len's concert",
                type=interactions.PresenceActivityType.WATCHING,
                emoji=interactions.emoji.Emoji(
                    id=1070778287644741642,
                    name="lenSeal"
                )
            )
        ],
        status=interactions.StatusType.IDLE
    )
)

database = r"database/database.csv"

jikan = AioJikan()


def snowflake_to_datetime(snowflake: int) -> datetime:
    timestamp_bin = bin(int(snowflake) >> 22)
    timestamp_dec = int(timestamp_bin, 0)
    timestamp_unix = (timestamp_dec + 1420070400000) / 1000

    return timestamp_unix

# CSV Layout is:
# Discord ID, Discord Username, Discord Joined, MAL Username, MAL ID, MAL Joined


def checkIfRegistered(discordId: int) -> bool:
    with open(database, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0] == discordId:
                return True
        return False


def saveToDatabase(discordId: int, discordUsername: str, discordJoined: int, malUsername: str, malId: int,
                   malJoined: int, registeredAt: int, registeredGuild: int, registeredBy: int, guildName: str):
    with open(database, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([discordId, discordUsername, discordJoined, malUsername,
                        malId, malJoined, registeredAt, registeredGuild, registeredBy, guildName])


def returnException(error: str):
    return f"""{EMOJI_UNEXPECTED_ERROR} **Error found!**
There's something wrong with the bot while processing your request.

Error is: {error}"""


async def checkClubMembership(username):
    jikanUser = await jikan.users(username=f'{username}', extension='clubs')
    return jikanUser['data']


async def getJikanData(uname):
    jikanData = await jikan.users(username=f'{uname}')
    jikanData = jikanData['data']
    return jikanData


async def searchJikanAnime(title: str):
    jikanParam = {
        'limit': '10'
    }
    jikanData = await jikan.search('anime', f'{title}', parameters=jikanParam)
    jikanData = jikanData['data']
    return jikanData


async def getJikanAnime(mal_id: int):
    id = mal_id
    jikanData = await jikan.anime(id)
    jikanData = jikanData['data']
    return jikanData


async def getNatsuAniApi(id, platform: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://aniapi.nattadasu.my.id/{platform}/{id}') as resp:
            jsonText = await resp.text()
            jsonFinal = jload(jsonText)
        await session.close()
        return jsonFinal


async def getKitsuMetadata(id, media: str = "anime"):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://kitsu.io/api/edge/{media}/{id}') as resp:
            jsonText = await resp.text()
            jsonFinal = jload(jsonText)
        await session.close()
        return jsonFinal


async def searchAniList(name: str = None, media_id: int = None, isAnime: bool = True):
    try:
        url = 'https://graphql.anilist.co'
        mediaType = 'ANIME' if isAnime else 'MANGA'
        variables = {
            'mediaType': mediaType.upper()
        }
        if name is not None:
            qs = '''query ($search: String, $mediaType: MediaType) {'''
            result = '''results: media(type: $mediaType, search: $search) {'''
            variables['search'] = name
        elif media_id is not None:
            qs = '''query ($mediaId: Int, $mediaType: MediaType) {'''
            result = '''results: media(type: $mediaType, id: $mediaId) {'''
            variables['mediaId'] = media_id
        else:
            raise ValueError("Either name or media_id must be provided")

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


async def searchSimklId(title_id: str, platform: str):
    url = f'https://api.simkl.com/search/id/?{platform}={title_id}&client_id={SIMKL_CLIENT_ID}'
    try:
        async with aiohttp.ClientSession() as sSession:
            async with sSession.get(url) as sResp:
                idFound = await sResp.json()
                fin = idFound[0]['ids']['simkl']
                await sSession.close()
                if idFound[0]['type'] != 'anime':
                    raise Exception('Not an anime')
                else:
                    return fin
    except:
        return 0


async def getSimklID(simkl_id: int, media_type: str):
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
                        "simkl": data.get('simkl', None),
                        "slug": data.get('slug', None),
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
                        "poster": animeFound.get('poster', None),
                        "fanart": animeFound.get('fanart', None)
                    }
                    await gSession.close()
                    return data
    except:
        data = {
            "simkl": None,
            "slug": None,
            "allcin": None,
            "anfo": None,
            "ann": None,
            "imdb": None,
            "mal": None,
            "offjp": None,
            "tmdb": None,
            "tvdb": None,
            "tvdbslug": None,
            "wikien": None,
            "wikijp": None,
            "poster": None,
            "fanart": None
        }
        return data


def trimCyno(message: str):
    if len(message) > 1000:
        msg = message[:1000]
        # trim spaces
        msg = msg.strip()
        return msg + "..."
    else:
        return message


async def generateMal(entry_id: int, isNsfw: bool = False):
    j = await getJikanAnime(entry_id)
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
    aa = await getNatsuAniApi(m, platform="myanimelist")
    aniApi = aa
    smId = await searchSimklId(m, 'mal')
    smk = await getSimklID(smId, 'anime')

    if j['synopsis'] is not None:
        # remove \n\n[Written by MAL Rewrite]
        jdata = j['synopsis'].replace("\n\n[Written by MAL Rewrite]", "")
        j_spl = jdata.split("\n")
        synl = len(j_spl)
        cynoin = j_spl[0]

        cynmo = f"\n> \n> Read more on [MyAnimeList](<https://myanimelist.net/anime/{m}>)"

        if len(str(cynoin)) >= 1000:
            cyno = trimCyno(cynoin)
            # when cyno has ... at the end, it means it's trimmed, then add read more
        else:
            cyno = cynoin
        if (cyno[-3:] == "...") or (synl > 1):
            cyno += cynmo

    else:
        cyno = "*None*"

    pdta = []
    if (smk['allcin'] is not None) and (smId != 0):
        pdta += [
            f"[<:allcinema:1079493870326403123>](http://www.allcinema.net/prog/show_c.php?num_c={smk['allcin']})"]
    if aa['aniDb'] is not None:
        pdta += [
            f"[<:aniDb:1073439145067806801>](<https://anidb.net/anime/{aa['aniDb']}>)"]
    if aa['aniList'] is not None:
        pdta += [
            f"[<:aniList:1073445700689465374>](<https://anilist.co/anime/{aa['aniList']}>)"]
    if aa['animePlanet'] is not None:
        pdta += [
            f"[<:animePlanet:1073446927447891998>](<https://www.anime-planet.com/anime/{aa['animePlanet']}>)"]
    if aniApi['aniSearch'] is not None:
        pdta += [
            f"[<:aniSearch:1073439148100300810>](<https://anisearch.com/anime/{aniApi['aniSearch']}>)"]
    if (smk['ann'] is not None) and (smId != 0):
        pdta += [
            f"[<:animeNewsNetwork:1079377192951230534>](<https://www.animenewsnetwork.com/encyclopedia/anime.php?id={smk['ann']}>)"]
    if (smk['imdb'] is not None) and (smId != 0):
        pdta += [
            f"[<:IMDb:1079376998880784464>](<https://www.imdb.com/title/{smk['imdb']}>)"]
    if aniApi['kaize'] is not None:
        pdta += [
            f"[<:kaize:1073441859910774784>](<https://kaize.io/anime/{aniApi['kaize']}>)"]
    if aniApi['kitsu'] is not None:
        pdta += [
            f"[<:kitsu:1073439152462368950>](<https://kitsu.io/anime/{aniApi['kitsu']}>)"]
    if aniApi['liveChart'] is not None:
        pdta += [
            f"[<:liveChart:1073439158883844106>](<https://livechart.me/anime/{aniApi['liveChart']}>)"]
    if aniApi['notifyMoe'] is not None:
        pdta += [
            f"[<:notifyMoe:1073439161194905690>](<https://notify.moe/anime/{aniApi['notifyMoe']}>)"]
    if aniApi['myAnimeList'] is not None:
        pdta += [
            f"[<:shikimori:1073441855645155468>](<https://shikimori.one/animes/{m}>)"]
    if smId != 0:
        pdta += [
            f"[<:simkl:1073630754275348631>](<https://simkl.com/anime/{smId}>)"]
    if aa['silverYasha'] is not None:
        pdta += [
            f"[<:silverYasha:1079380182059733052>](<https://db.silveryasha.web.id/anime/{aa['silverYasha']}>)"]
    if (smk['tmdb'] is not None) and (smId != 0):
        if j['type'] == "TV":
            aniType = "tv"
        else:
            aniType = "movie"
        pdta += [
            f"[<:tmdb:1079379319920529418>](<https://www.themoviedb.org/tv/{smk['tmdb']}>)"]
    if (smk['tvdb'] is not None) and (smId != 0):
        if j['type'] == "TV":
            aniType = "series"
        else:
            aniType = "movies"
        pdta += [
            f"[<:tvdb:1079378495064510504>](<https://www.thetvdb.com/?tab={aniType}&id={smk['tvdb']}>)"]
    elif (smk['tvdbslug'] is not None) and (smId != 0):
        if j['type'] == "TV":
            aniType = "series"
        else:
            aniType = "movies"
        pdta += [
            f"[<:tvdb:1079378495064510504>](<https://www.thetvdb.com/{aniType}/{smk['tvdbslug']}>)"]

    if len(pdta) > 0:
        pdta = " ".join(pdta)
        pdta = "\n**External sites**\n" + pdta
    else:
        pdta = ""

    if (smId != 0) and (smk['poster'] is not None):
        poster = f"https://simkl.in/posters/{smk['poster']}_m.webp"
        background = f"https://simkl.in/fanart/{smk['fanart']}_w.webp"
        note = "Images from SIMKL"
    elif (aa['kitsu'] != 0) or (aa['kitsu'] is not None):
        kitsu = await getKitsuMetadata(aa['kitsu'], 'anime')
        post = kitsu['data']['attributes']['posterImage']['original']
        if post is not None:
            poster = post
            background = kitsu['data']['attributes']['coverImage']['original']
            note = "Images from Kitsu"
        else:
            poster = j['images']['jpg']['image_url']
            background = ""
            note = ""
    else:
        poster = j['images']['jpg']['image_url']
        background = ""
        note = ""

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
        tgs = sorted(set(tgs))
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

    # start date logic
    if astn is not None:
        # Check if title is airing/aired or TBA by checking astr in regex
        if re.match(r'^([\d]{4})', astr) or re.match(r'^([a-zA-Z]{3} [\d]{4})', astr):
            ast = astr.split(" to ")[0]
            tsa = ""
        elif re.match(r'^([a-zA-Z]{3} [\d]{1,2}, [\d]{4})', astr):
            if (bcast['string'] == "Unknown") or (bcast['string'] is None):
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
            if (bcast['string'] == "Unknown") or (bcast['string'] is None):
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

    # # create a synonyms list
    syns = []
    for s in j['titles']:
        syns += [s['title']]
    ogt = [j['title_english'], j['title_japanese'], j['title']]
    syns = [x for x in syns if x not in ogt]
    # sort
    syns = sorted(set(syns))
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

    rot = j['title']

    ent = j['title_english']
    if (ent == '') or (ent is None):
        ent = rot

    nat = j['title_japanese']
    if (nat == '') or (nat is None):
        nat = "*None*"

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
{pdta}
""",
        color=0x2E51A2,
        thumbnail=interactions.EmbedImageStruct(
            url=poster
        ),
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
                value=syns
            ),
            interactions.EmbedField(
                name="Genres and Themes",
                value=tgs
            ),
            interactions.EmbedField(
                name="Episodes",
                value=eps,
                inline=True
            ),
            interactions.EmbedField(
                name="Durations",
                value=dur,
                inline=True
            ),
            interactions.EmbedField(
                name="Status",
                value=stat,
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


async def generateAnilist(alm: dict, isNsfw: bool = False, bypassEcchi: bool = False):
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
        enChkMark = '\\*'
    else:
        enChkMark = ''
    nat = alm['title']['native']
    if nat is None:
        nat = "*None*"

    ogt = [rot, ent, nat]
    syns = [x for x in syns if x not in ogt]
    # sort
    syns = sorted(set(syns))
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

    poster = alm['coverImage']['large']
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

        if len(str(cynoin)) >= 1000:
            cyno = trimCyno(cynoin)
        else:
            cyno = cynoin

        if (cyno[-3:] == "...") or (cynl > 1):
            cyno += f"\n> \n> [Read more on AniList](<https://anilist.co/manga/{id}>)"
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
            cw = False
        elif (t['name'] in bannedTags) and (isNsfw is True):
            if t['isMediaSpoiler'] is True:
                tgs += [f"||{t['name']} **!**||"]
            else:
                tgs += [f"{t['name']} **!** "]
            cw = True
        else:
            syChkMark = '*'

    if len(tgs) is None:
        tgs = "*None*"
    elif len(tgs) > 0:
        tgs = sorted(set(tgs))
        tgs = ", ".join(tgs)

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


async def bypassAniListEcchiTag(alm: dict):
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


async def getParentNsfwStatus(snowflake: int):
    botHttp = interactions.HTTPClient(token=BOT_TOKEN)
    guild = await botHttp.get_channel(channel_id=snowflake)
    # close the connection
    return guild['nsfw']


async def getUserData(user_snowflake: int):
    botHttp = interactions.HTTPClient(token=BOT_TOKEN)
    member = await botHttp.get_user(user_id=user_snowflake)
    # close the connection
    return member


async def getGuildMemberData(guild_snowflake: int, user_snowflake: int):
    botHttp = interactions.HTTPClient(token=BOT_TOKEN)
    member = await botHttp.get_member(guild_id=guild_snowflake, member_id=user_snowflake)
    return member


async def getNekomimi(gender: str = None):
    nmDb = pd.read_csv("database/nekomimiDb.tsv", sep="\t")
    nmDb = nmDb.fillna('')
    if gender is not None:
        query = nmDb[nmDb['girlOrBoy'] == f'{gender}']
    else:
        query = nmDb
    # get a random row from the query
    row = query.sample()
    return row


# START OF BOT CODE

@bot.command(
    name="ping",
    description="Ping the bot!"
)
async def ping(ctx: interactions.CommandContext):
    # create a time var when the command invoked
    start = time.perf_counter()
    await ctx.defer()  # to make sure if benchmark reflects other commands with .defer()
    # send a message to the channel
    await ctx.send(f"{EMOJI_ATTENTIVE} Pong!")
    # get the time when the message was sent
    end = time.perf_counter()
    # calculate the time it took to send the message
    duration = (end - start) * 1000
    # if durations is above 1000ms, show additional message
    if duration > 2500:
        msg = f"{EMOJI_FORBIDDEN} Whoa, that's so slow! Please contact the bot owner!"
    elif duration > 1000:
        msg = f"{EMOJI_DOUBTING} That's slow! But don't worry, it's still working!"
    else:
        msg = f"{EMOJI_SUCCESS} I'm working as intended!"
    # send a message to the channel
    await ctx.edit(f"{EMOJI_ATTENTIVE} Pong! Response time: {duration:.2f}ms\n{msg}")


@bot.command(
    name="register",
    description="Register your MAL profile to the bot!",
    # type=interactions.InteractionType.PING,
    options=[
        interactions.Option(
            name="mal_username",
            description="Your MAL username",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="accept_gdpr",
            description="Allow the bot to store your data: MAL Uname, UID, Discord Uname, UID, Joined Date",
            type=interactions.OptionType.BOOLEAN,
            required=True
        )
    ]
)
async def register(ctx: interactions.CommandContext, mal_username: str, accept_gdpr: bool):
    await ctx.defer(ephemeral=True)
    # check if user accepted GDPR
    if accept_gdpr is False:
        messages = f"""**You have not accepted the GDPR/CCPA/CPRA Privacy Consent!**
Unfortunately, we cannot register you without your consent. However, you can still use the bot albeit limited.

Allowed commands:
- `/profile mal_username:<str>`
- `/ping`

If you want to register, please use the command `/register` again and accept the consent by set the `accept_gdpr` option to `true`!

We only store your MAL username, MAL UID, Discord username, Discord UID, and joined date for both platforms, also server ID during registration.
We do not store any other data such as your email, password, or any other personal information.
We also do not share your data with any third party than necessary, and it only limited to the required platforms such Username.

***We respect your privacy.***

For more info what do we collect and use, use `/privacy`.
"""
        await ctx.send(messages, ephemeral=True)
        return
    else:
        # get the message author username
        messageAuthor = ctx.user
        # get the message author id
        discordId = str(messageAuthor.id)
        # get user discriminator
        discordDiscrim = str(messageAuthor.discriminator)
        # get user joined date
        discordJoined = snowflake_to_datetime(discordId)
        discordJoined = int(discordJoined)
        discordServerName = ctx.guild.name

        clubId = CLUB_ID

        # check if user is already registered
        if checkIfRegistered(discordId):
            messages = f"""{EMOJI_DOUBTING} **You are already registered!**"""
            if str(ctx.guild_id) == f'{VERIFICATION_SERVER}':
                messages += f'''\nTo get your role back, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={clubId}>)!'''
        else:
            # get user id from jikan
            try:
                uname = mal_username.strip()
                jikanUser = await getJikanData(uname)
                uname = jikanUser['username']
                # convert joined date to epoch
                jikanUser['joined'] = jikanUser['joined'].replace(
                    "+00:00", "+0000")
                joined = datetime.datetime.strptime(
                    jikanUser['joined'], "%Y-%m-%dT%H:%M:%S%z")
                joined = joined.timestamp()
                # try remove decimal places from joined
                joined = int(joined)
                registered = datetime.datetime.now().timestamp()
                registered = int(registered)
                messages = f"""{EMOJI_SUCCESS} **Your account has been registered!** :tada:

**Discord Username**: {messageAuthor}#{discordDiscrim} `{discordId}`
**Discord Joined date**: <t:{discordJoined}:F>
———————————————————————————————
**MyAnimeList Username**: [{uname}](<https://myanimelist.net/profile/{uname}>) `{jikanUser['mal_id']}`
**MyAnimeList Joined date**: <t:{joined}:F>"""
                if str(ctx.guild_id) == f'{VERIFICATION_SERVER}':
                    messages += f'''\n
*Now, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={clubId}>) to get your role!*'''
                saveToDatabase(discordId, f'{messageAuthor}#{discordDiscrim}', discordJoined,
                               uname, jikanUser['mal_id'], joined, registered, int(ctx.guild_id), discordId, discordServerName)
            except Exception as e:
                messages = returnException(e)

        await ctx.send(messages, ephemeral=True)


@bot.command(
    name="verify",
    description="Verify your MAL profile to this server!",
    # type=interactions.InteractionType.PING
    scope=[
        int(VERIFICATION_SERVER)
    ]
)
async def verify(ctx: interactions.CommandContext):
    await ctx.defer()
    # get the message author username
    messageAuthor = ctx.user
    # get the message author id
    discordId = str(messageAuthor.id)
    # get user joined date
    discordJoined = snowflake_to_datetime(discordId)
    discordJoined = int(discordJoined)
    getMemberDetail = await ctx.guild.get_member(discordId)
    memberRoles = getMemberDetail.roles
    verifiedRole = VERIFIED_ROLE

    clubId = CLUB_ID

    if str(ctx.guild_id) != f"{VERIFICATION_SERVER}":
        messages = f"""{EMOJI_USER_ERROR} **You are not allowed to use this command!**
This command only allowed to be used on that particular server.... if you know who's the bot owner is"""
    # check if user is already obtained role
    elif int(verifiedRole) in memberRoles:
        messages = f"""{EMOJI_USER_ERROR} **You are already verified!**"""
    else:
        # check if user is already registered
        if checkIfRegistered(discordId):
            # Grab user's MAL username from database
            with open(database, "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if row[0] == discordId:
                        username = row[3]
                        break
            # Check club membership
            clubs = await checkClubMembership(username)
            verified = False
            for club in clubs:
                if int(club['mal_id']) == int(CLUB_ID):
                    await ctx.member.add_role(verifiedRole)
                    messages = f"""{EMOJI_ATTENTIVE} **You have been verified!**"""
                    verified = True
                    # exit the loop
                    break
            if verified is False:
                messages = f"""{EMOJI_USER_ERROR} **You are not in the club!**
Please join [our club](<https://myanimelist.net/clubs.php?cid={clubId}>) to get your role!"""
        else:
            messages = f"""{EMOJI_DOUBTING} **You are not registered!**
Please use the command `/register` to register your MAL profile to this server!"""

    await ctx.send(messages)


@bot.command(
    name="whois",
    description="Get user's data!",
    # type=interactions.InteractionType.PING,
    options=[
        interactions.Option(
            name="user",
            description="The user to get data from",
            type=interactions.OptionType.USER,
            required=True
        )
    ]
)
async def whois(ctx: interactions.CommandContext, user: int):
    await ctx.defer()

    try:
        if checkIfRegistered(user.id):
            with open(database, "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if row[0] == user.id:
                        # escape markdown
                        row[1] = row[1].replace("*", "\\*").replace("_", "\\_").replace("~", "\\~").replace("`", "\\`").replace(
                            "|", "\\|").replace(">", "\\>").replace("<", "\\<").replace("@", "\\@")
                        row[3] = row[3].replace("_", "\\_")
                        if row[8] != user.id:
                            assistedRegister = f"\nRegistered by: <@!{row[8]}>"
                        else:
                            assistedRegister = ""
                        userData = await getUserData(user_snowflake=row[0])
                        userJoined = await getGuildMemberData(guild_snowflake=ctx.guild_id, user_snowflake=row[0])
                        userJoined = datetime.datetime.strptime(
                            userJoined['joined_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
                        userJoined = int(userJoined.timestamp())
                        userAvatar: str = userData['avatar']
                        # check if avatar has a_ prefix
                        if userAvatar.startswith("a_"):
                            fileExt = "gif"
                        else:
                            fileExt = "webp"
                        userBanner: str = userData['banner']
                        userDecColor = userData['accent_color']
                        messages = ""
                        dcEm = interactions.Embed(
                            title=f"{user.username}#{user.discriminator} data",
                            thumbnail=interactions.EmbedImageStruct(
                                url=f"https://cdn.discordapp.com/avatars/{user.id}/{userAvatar}.{fileExt}?size=512"
                            ),
                            color=userDecColor,
                            fields=[
                                interactions.EmbedField(
                                    name="Discord",
                                    value=f"""Username: {row[1]}
Snowflake: `{row[0]}`
Created date: <t:{row[2]}:F>
Joined to {ctx.guild.name}: <t:{userJoined}:F>""",
                                ),
                                interactions.EmbedField(
                                    name="Bot Database",
                                    value=f"""Registered date: <t:{row[6]}:F>
Registered in: {row[9]}
Server Snowflake: `{row[7]}`{assistedRegister}"""
                                ),
                                interactions.EmbedField(
                                    name="MyAnimeList",
                                    value=f"""Username: [{row[3]}](<https://myanimelist.net/profile/{row[3]}>) ([Anime List](<https://myanimelist.net/animelist/{row[3]}>) | [Manga List](<https://myanimelist.net/mangalist/{row[3]}>))
User ID: `{row[4]}`
Created date: <t:{row[5]}:F>"""
                                )
                            ],
                            image=interactions.EmbedImageStruct(
                                url=f"https://cdn.discordapp.com/banners/{row[0]}/{userBanner}.webp?size=512"
                            )
                        )
                        break

        else:
            messages = f"<@!{user.id}> data is not registered, trying to get only Discord data..."
            userData = await getUserData(user_snowflake=user.id)
            userJoined = await getGuildMemberData(guild_snowflake=ctx.guild_id, user_snowflake=user.id)
            userJoined = datetime.datetime.strptime(
                userJoined['joined_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
            userJoined = int(userJoined.timestamp())
            userAvatar: str = userData['avatar']
            # check if avatar has a_ prefix
            if userAvatar.startswith("a_"):
                fileExt = "gif"
            else:
                fileExt = "webp"
            userBanner: str = userData['banner']
            userDecColor = userData['accent_color']
            dcEm = interactions.Embed(
                title=f"{user.username}#{user.discriminator} data",
                color=userDecColor,
                fields=[
                    interactions.EmbedField(
                        name="Discord",
                        value=f"""Username: {user.username}#{user.discriminator}
Snowflake: `{user.id}`
Created date: <t:{int(snowflake_to_datetime(user.id))}:F>
Joined to {ctx.guild.name}: <t:{userJoined}:F>"""
                    )
                ],
                thumbnail=interactions.EmbedImageStruct(
                    url=f"https://cdn.discordapp.com/avatars/{user.id}/{userAvatar}.{fileExt}?size=512"
                ),
                image=interactions.EmbedImageStruct(
                    url=f"https://cdn.discordapp.com/banners/{user.id}/{userBanner}.webp?size=512"
                )
            )

        sendMessages = messages
    except AttributeError:
        sendMessages = ""
        dcEm = interactions.Embed(
            color=0xff0000,
            title="Error",
            description=returnException(
                "User can not be found if they're joined this server or not.")
        )
    except Exception as e:
        sendMessages = ""
        dcEm = interactions.Embed(
            color=0xff0000,
            title="Error",
            description=returnException(e)
        )

    await ctx.send(sendMessages, embeds=dcEm)


@bot.command(
    name="profile",
    description="Get your MAL profile!",
    # type=interactions.InteractionType.PING
    options=[
        interactions.Option(
            name="user",
            description="The user to get data from by looking up",
            type=interactions.OptionType.USER,
            required=False
        ),
        interactions.Option(
            name="mal_username",
            description="The user to get data from using MAL username",
            type=interactions.OptionType.STRING,
            required=False
        ),
        interactions.Option(
            name="extended",
            description="Extend embed result, show your anime/manga stats and useful links",
            type=interactions.OptionType.BOOLEAN,
            required=False
        )
    ]
)
async def profile(ctx: interactions.CommandContext, user: int = None, mal_username: str = None, extended: bool = False):
    await ctx.defer()

    userRegistered = f"{EMOJI_DOUBTING} **You are looking at your own profile!**\nYou can also use </profile:1072608801334755529> without any arguments to get your own profile!"
    httpErr = "If you get HTTP 503 or HTTP 408 error, resubmit command again!\nUsually, first time use on Jikan would take a time to fetch your data"

    def generate_embed(uname: str, uid: int, malAnime: dict, malManga: dict, lastOnline: int, joined: int, bday: int = None, extend: bool = False):
        bbd = ""
        if bday is not None:
            # convert bday from timestamp back to datetime
            bdayRaw = datetime.datetime.fromtimestamp(int(bday))
            today = datetime.datetime.now(tz=datetime.timezone.utc)
            currYear = today.year
            upcoming = bdayRaw.replace(year=currYear)
            if int(upcoming.timestamp()) < int(today.timestamp()):
                upcoming = upcoming.replace(year=currYear + 1)
            bbd = f"\nBirthday: <t:{int(bday)}:D> <t:{int(bday)}:R> (next birthday <t:{int(upcoming.timestamp())}:R>)"
        desc = f"[Anime List](https://myanimelist.net/animelist/{uname}) | [Manga List](https://myanimelist.net/mangalist/{uname})"
        fds = [
            interactions.EmbedField(
                name="Profile",
                value=f"""User ID: `{malProfile['mal_id']}`
Account created: <t:{joined}:D> (<t:{joined}:R>)
Last online: <t:{lastOnline}:R>{bbd}""",
                inline=False
            )
        ]
        img = None
        foo = "Powered by MyAnimeList (via Jikan). Data may be inaccurate due to Jikan caching. To see more information, append \"extended: True\" argument!"
        if extend is True:
            desc += f"\nSee also on 3rd party sites: [MAL Badges](https://mal-badges.com/users/{uname}), [anime.plus malgraph](https://anime.plus/{uname})"
            fds += [
                interactions.EmbedField(
                    name="Anime Stats",
                    value=f"""• Days watched: {malAnime['days_watched']}
• Mean score: {malAnime['mean_score']}
• Total entries: {malAnime['total_entries']}
👀 {malAnime['watching']} | ✅ {malAnime['completed']} | ⏸️ {malAnime['on_hold']} | 🗑️ {malAnime['dropped']} | ⏰ {malAnime['plan_to_watch']}
*Episodes watched: {malAnime['episodes_watched']}""",
                    inline=True
                ),
                interactions.EmbedField(
                    name="Manga Stats",
                    value=f"""• "Days" read: {malManga['days_read']}
• Mean score: {malManga['mean_score']}
• Total entries: {malManga['total_entries']}
👀 {malManga['reading']} | ✅ {malManga['completed']} | ⏸️ {malManga['on_hold']} | 🗑️ {malManga['dropped']} | ⏰ {malManga['plan_to_read']}
*Chapters read: {malManga['chapters_read']}*
*Volumes read: {malManga['volumes_read']}*""",
                    inline=True
                )
            ]
            img = interactions.EmbedImageStruct(
                url=f"https://malheatmap.com/users/{uname}/signature"
            )
            foo = "Powered by MyAnimeList (via Jikan) and MAL Heatmap. Data may be inaccurate due to Jikan caching."
        else:
            desc += f"\nTotal Anime: {malAnime['total_entries']} (⭐ {malAnime['mean_score']}) | Total Manga: {malManga['total_entries']} (⭐ {malManga['mean_score']})"

        if re.search(r"s$", uname):
            ttl = f"{uname}' MAL Profile"
        else:
            ttl = f"{uname}'s MAL Profile"

        embed = interactions.Embed(
            author=interactions.EmbedAuthor(
                name="MyAnimeList Profile",
                url="https://myanimelist.net",
                icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png"
            ),
            title=ttl,
            url=f"https://myanimelist.net/profile/{uname}",
            description=desc,
            thumbnail=interactions.EmbedImageStruct(
                url=f"https://cdn.myanimelist.net/images/userimages/{uid}.jpg"
            ),
            color=0x2E51A2,
            fields=fds,
            image=img,
            footer=interactions.EmbedFooter(
                text=foo
            )
        )
        return embed

    if user and mal_username:
        sendMessages = ""
        dcEm = interactions.Embed(
            title="Error",
            description=returnException(
                f"{EMOJI_USER_ERROR} **You cannot use both options!**"),
            color=0xFF0000
        )
    if mal_username is None:
        if user is not None:
            uid = user.id
        else:
            uid = ctx.author.id
        try:
            if checkIfRegistered(uid):
                with open(database, "r") as f:
                    reader = csv.reader(f, delimiter="\t")
                    for row in reader:
                        if row[0] == uid:
                            jikanStats = await jikan.users(username=row[3], extension='full')
                            malProfile = jikanStats['data']
                            mun = malProfile['username'].replace("_", "\\_")
                            mid = malProfile['mal_id']
                            ani = malProfile['statistics']['anime']
                            man = malProfile['statistics']['manga']
                            bth = None
                            if malProfile['birthday'] is not None:
                                bth = malProfile['birthday'].replace("+00:00", "+0000")
                                bth = int(datetime.datetime.strptime(bth, "%Y-%m-%dT%H:%M:%S%z").timestamp())
                            lstOnline = malProfile['last_online'].replace("+00:00", "+0000")
                            lstOnline = int(datetime.datetime.strptime(lstOnline, "%Y-%m-%dT%H:%M:%S%z").timestamp())
                            dtJoin = malProfile['joined'].replace("+00:00", "+0000")
                            dtJoin = int(datetime.datetime.strptime(dtJoin, "%Y-%m-%dT%H:%M:%S%z").timestamp())

                            dcEm = generate_embed(uname=mun, uid=mid, malAnime=ani, malManga=man, lastOnline=lstOnline, joined=dtJoin, bday=bth, extend=extended)
                            if user is None:
                                sendMessages = ""
                            elif ctx.author.id == uid:
                                sendMessages = userRegistered
                            else:
                                sendMessages = f"<@{uid}> data:"
            else:
                if user is None:
                    regAccount = f"{EMOJI_USER_ERROR} Sorry, but to use standalone command, you need to `/register` your account. Or, you can use `/profile mal_username:<yourUsername>` instead"
                    foo = "Please be a good child, okay? 🚶‍♂️"
                else:
                    regAccount = f"I couldn't find <@!{uid}> on my database. It could be that they have not registered their MAL account yet."
                    foo = ""
                sendMessages = ""
                dcEm = interactions.Embed(
                    title="User have not registered yet!",
                    description=returnException(regAccount),
                    color=0xFF0000,
                    footer=interactions.EmbedFooter(
                        text=foo
                    )
                )
        except Exception as e:
            sendMessages = ""
            dcEm = interactions.Embed(
                title="Error",
                description=returnException(e),
                color=0xFF0000,
                footer=interactions.EmbedFooter(
                    text=httpErr
                )
            )
    elif mal_username is not None:
        uname = mal_username.strip()
        try:
            with open(database, "r") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if (str(row[3]).lower() == str(uname).lower()) and (ctx.author.id == row[0]):
                        sendMessages = userRegistered
                        break
                    elif (str(row[3]).lower() == str(uname).lower()) and (ctx.author.id != row[0]):
                        sendMessages = f"{EMOJI_ATTENTIVE} This MAL account is registered on this bot, you could use `/profile user:<@!{row[0]}>` instead"
                        break
                    else:
                        sendMessages = ""
            jikanStats = await jikan.users(username=uname, extension='full')
            malProfile = jikanStats['data']
            mun = malProfile['username'].replace("_", "\\_")
            mid = malProfile['mal_id']
            ani = malProfile['statistics']['anime']
            man = malProfile['statistics']['manga']
            bth = None
            if malProfile['birthday'] is not None:
                bth = malProfile['birthday'].replace("+00:00", "+0000")
                bth = int(datetime.datetime.strptime(bth, "%Y-%m-%dT%H:%M:%S%z").timestamp())
            lstOnline = malProfile['last_online'].replace("+00:00", "+0000")
            lstOnline = int(datetime.datetime.strptime(lstOnline, "%Y-%m-%dT%H:%M:%S%z").timestamp())
            dtJoin = malProfile['joined'].replace("+00:00", "+0000")
            dtJoin = int(datetime.datetime.strptime(dtJoin, "%Y-%m-%dT%H:%M:%S%z").timestamp())

            dcEm = generate_embed(uname=mun, uid=mid, malAnime=ani, malManga=man, lastOnline=lstOnline, joined=dtJoin, bday=bth, extend=extended)
        except Exception as e:
            sendMessages = ""
            dcEm = interactions.Embed(
                title="Error",
                description=returnException(e),
                color=0xFF0000,
                footer=interactions.EmbedFooter(
                    text=httpErr
                )
            )

    await ctx.send(sendMessages, embeds=dcEm)


@bot.command(
    name="unregister",
    description="Unregister your MAL account from the bot!",
)
async def unregister(ctx: interactions.CommandContext):
    if checkIfRegistered(ctx.author.id):
        # use pandas to read and drop the row
        try:
            df = pd.read_csv(database, sep="\t")
            df_drop = df.drop(df.query(f"discordId=={ctx.author.id}").index)
            df_drop.to_csv(database, sep="\t", index=False, encoding='utf-8')
            sendMessages = f"""{EMOJI_SUCCESS} **Successfully unregistered!**"""
        except Exception as e:
            sendMessages = returnException(e)
    else:
        sendMessages = f"""{EMOJI_USER_ERROR} **You are not registered!**"""

    await ctx.send(sendMessages, ephemeral=True)


@bot.command(
    name="about",
    description="Show information about this bot!"
)
async def about(ctx: interactions.CommandContext):
    ownerUserUrl = f'https://discord.com/users/{AUTHOR_USERID}'
    messages = f'''<@!{BOT_CLIENT_ID}> is a bot personally created and used by [nattadasu](<https://nattadasu.my.id>) with the initial purpose as for member verification and MAL profile integration bot, which is distributed under [AGPL 3.0](<https://www.gnu.org/licenses/agpl-3.0.en.html>) license. ([Source Code](<https://github.com/nattadasu/ryuuRyuusei>), source will be older than production)

However, due to how advanced the bot in querying information regarding user, anime on MAL, and manga on AniList, invite link is available for anyone who's interested to invite the bot (see `/invite`).

This bot may requires your consent to collect and store your data when you invoke `/register` command. You can see the privacy policy by using `/privacy` command.

However, you still able to use the bot without collecting your data, albeit limited usage.

If you want to contact the author, send a DM to [{AUTHOR_USERNAME}](<{ownerUserUrl}>) or via [support server](<{BOT_SUPPORT_SERVER}>).
'''
    await ctx.send(messages)


@bot.command(
    name="privacy",
    description="Read privacy policy of this bot, especially for EU (GDPR) and California (CPRA/CCPA) users!"
)
async def privacy(ctx: interactions.CommandContext):
    messages = '''Hello and thank you for your interest to read this tl;dr version of Privacy Policy.

In this message we shortly briefing which content we collect, store, and use, including what third party services we used for bot to function as expected.

__We collect, store, and use following data__:
- Discord: username, discriminator, user ID, joined date, guild/server ID of registration, server name, date of registration, user referral (if any)
- MyAnimeList: username, user ID, joined date

__We do not collect, however, following data__:
- Logs of messages sent by system. Logging only will be enabled during development, testing, or maintenance.

Data stored locally to Data Maintainer's (read: owner) server/machine of this bot. To read your profile that we've collected, type `/export_data` following your username.

__We used following modules/technology for the bot__:
- ✨ [AniList](<https://anilist.co>) API
- [Discord](<https://discord.com>), through [Python: `interactions.py`](<https://github.com/interactions-py/interactions.py>).
- [MyAnimeList](<https://myanimelist.net>), through [Jikan](<https://jikan.moe/>) (Python: `jikanpy`) and [MAL Heatmap](<https://malheatmap.com>).
- ✨ [nattadasu's AnimeApi Relation](<https://aniapi.nattadasu.my.id>).
- ✨ [nattadasu's nekomimiDb](<https://github.com/nattadasu/nekomimiDb>).

As user, you have right to create a profile by typing `/register` and accept privacy consent and/or modify/delete your data by typing `/unregister`.

For any contact information, type `/about`.

✨: No data is being transmitted about you than bot's IP address and/or query request.'''

    await ctx.send(messages, ephemeral=True)


@bot.command(
    name="export_data",
    description="Export your data from the bot, made for GDPR, CPRA, LGDP users!",
)
async def export_data(ctx: interactions.CommandContext):
    await ctx.defer(ephemeral=True)
    userId = ctx.author.id
    if checkIfRegistered(userId):
        with open(database, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if row[0] == 'discordId':
                    header = row
                    continue
                if row[0] == str(userId):
                    row[0] = int(row[0])
                    row[2] = int(row[2])
                    row[4] = int(row[4])
                    row[5] = int(row[5])
                    row[6] = int(row[6])
                    row[7] = int(row[7])
                    row[8] = int(row[8])
                    row[9] = str(row[9])
                    userRow = row
                    userRow = dict(zip(header, userRow))
                    userRow = json.dumps(userRow)
                    dcEm = interactions.Embed(
                        title="Data Exported!",
                        description=f"""{EMOJI_SUCCESS} **Here's your data!**
```json
{userRow}
```or, do you prefer Python list format?```python
{{{header},
{row}}}```""",
                        color=0x2E2E2E,
                        footer=interactions.EmbedFooter(
                            text="Unregister easily by typing /unregister!"
                        )
                    )
                    messages = None
                    break
    else:
        messages = f"""{EMOJI_USER_ERROR} **You are not registered!**"""
        dcEm = None

    await ctx.send(messages, embeds=dcEm, ephemeral=True)


@bot.command(
    name="anime",
    description="Get anime information from MAL and AniAPI"
)
async def anime(ctx: interactions.CommandContext):
    pass


@anime.subcommand()
@interactions.option(
    name="title",
    description="The anime title name to search",
    type=interactions.OptionType.STRING,
    required=True
)
async def search(ctx: interactions.CommandContext, title: str = None):
    """Search anime from MAL by title. Anime lookup powered by AniList"""
    await ctx.defer()
    await ctx.get_channel()

    async def lookupByNameAniList(aniname: str):
        rawData = await searchAniList(name=aniname, media_id=None, isAnime=True)
        return rawData[0]

    async def lookupByNameJikan(name: str):
        rawData = await searchJikanAnime(name)
        for ani in rawData:
            romaji = ani['title']
            english = ani['title_english']
            native = ani['title_japanese']
            syns = ani['titles']
            myAnimeListID = ani['mal_id']
            if (romaji == name) or (english == name) or (native == name):
                return myAnimeListID
            else:
                for title in syns:
                    if title == name:
                        return myAnimeListID

    try:
        alData = await lookupByNameAniList(title)
        ani_id = alData['idMal']
    except:
        ani_id = None

    if ani_id is None:
        try:
            ani_id = await lookupByNameJikan(title)
        except:
            ani_id = None

    if ani_id is not None:
        try:
            # check if command invoked in a forum thread
            if ctx.channel.type == 11 or ctx.channel.type == 12:
                # get parent channel id
                prId = ctx.channel.parent_id
                # get NSFW status
                nsfw_bool = await getParentNsfwStatus(snowflake=prId)
            else:
                nsfw_bool = ctx.channel.nsfw
            dcEm = await generateMal(ani_id, nsfw_bool)
            sendMessages = None
        except Exception as e:
            sendMessages = returnException(e)
            dcEm = None
    else:
        sendMessages = returnException(
            "We couldn't able to find any anime with that title.")
        dcEm = None

    await ctx.send(sendMessages, embeds=dcEm)


@anime.subcommand()
async def random(ctx: interactions.CommandContext):
    """Get random anime information from MAL"""
    await ctx.defer()
    await ctx.get_channel()

    async def lookupRandom():
        # open database/mal.csv
        df = pd.read_csv("database/mal.csv", sep="\t")
        # get random anime
        randomAnime = df.sample()
        # get anime id
        randomAnimeId: int = randomAnime['mal_id'].values[0]
        return randomAnimeId

    ani_id = await lookupRandom()

    try:
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        sendMessages = await generateMal(ani_id, nsfw_bool)
    except Exception as e:
        sendMessages = returnException(e)

    await ctx.send(sendMessages)


@anime.subcommand()
@interactions.option(
    name="id",
    description="The anime ID on MAL to fetch",
    type=interactions.OptionType.INTEGER,
    required=True
)
async def info(ctx: interactions.CommandContext, id: int):
    """Get anime information from MAL and AniAPI using MAL id"""
    await ctx.defer()
    await ctx.get_channel()
    try:
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        dcEm = await generateMal(id, nsfw_bool)
        sendMessages = None
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None

    await ctx.send(sendMessages, embeds=dcEm)


@anime.subcommand(
    options=[
        interactions.Option(
            name="id",
            description="The anime ID on the platform to search",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="platform",
            description="The platform to search",
            type=interactions.OptionType.STRING,
            choices=[
                interactions.Choice(
                    name="aniDB",
                    value="anidb"
                ),
                interactions.Choice(
                    name="AniList",
                    value="anilist"
                ),
                interactions.Choice(
                    name="Anime-Planet",
                    value="animeplanet"
                ),
                interactions.Choice(
                    name="aniSearch",
                    value="anisearch"
                ),
                interactions.Choice(
                    name="Kaize (BETA, slug only)",
                    value="kaize"
                ),
                interactions.Choice(
                    name="Kitsu (only ID supported)",
                    value="kitsu"
                ),
                interactions.Choice(
                    name="LiveChart",
                    value="livechart"
                ),
                interactions.Choice(
                    name="MyAnimeList",
                    value="myanimelist"
                ),
                interactions.Choice(
                    name="Notify.moe",
                    value="notify"
                ),
                interactions.Choice(
                    name="Shikimori (Шикимори)",
                    value="shikimori"
                ),
                interactions.Choice(
                    name="SIMKL",
                    value="simkl"
                )
            ],
            required=True
        )
    ]
)
async def relations(ctx: interactions.CommandContext, id: str, platform: str):
    """Find a list of relations to external site for an anime"""
    await ctx.defer()
    try:
        uid = id
        pf = platform
        # Fix platform name
        if platform == 'shikimori':
            pf = 'myanimelist'
            # remove any prefix started with any a-z in the id
            uid = re.sub(r'^[a-z]+', '', id)
        elif platform == 'simkl':
            simId = uid

        if pf == 'simkl':
            simDat = await getSimklID(simkl_id=simId, media_type='anime')
            # if simDat['mal'] key is not in the dict, it will raise KeyError
            try:
                uid = simDat['mal']
                pf = 'myanimelist'
            except KeyError:
                raise Exception(
                    "No MAL ID found, please ask the SIMKL developer to add it to the database")

        await ctx.send(f"Searching for relations on {platform} using ID: {uid}")

        if pf == 'kaize':
            try:
                try:
                    aa = await getNatsuAniApi(id=uid, platform=pf)
                except:
                    # check on slug using regex, if contains `-N` suffix, try to decrease by one,
                    # if `-N` is `-1`, remove completely the slug
                    # get the last number
                    lastNum = re.search(r'\d+$', uid).group()
                    # get the slug
                    slug = re.sub(r'-\d+$', '', uid)
                    # decrease the number by one
                    lastNum = int(lastNum) - 1
                    # if the number is 0, remove the suffix
                    if lastNum == 0:
                        uid = slug
                    else:
                        uid = f"{slug}-{lastNum}"
                    await ctx.edit(f"Searching for relations on {platform} using ID: {uid} (decrease by one)")
                    aa = await getNatsuAniApi(id=uid, platform=pf)
            except json.JSONDecodeError:
                raise Exception("""We've tried to search for the anime using the slug (and even fix the slug itself), but it seems that the anime is not found on Kaize via AnimeApi.
Please send a message to AnimeApi maintainer, nattadasu (he is also a developer of this bot)""")
        else:
            aa = await getNatsuAniApi(id=uid, platform=pf)

        # Get the anime title
        title = aa['title']

        # Get the relations from others to SIMKL, if MAL is found
        if platform != 'simkl':
            try:
                if aa['myAnimeList'] is not None:
                    # search SIMKL ID
                    simId = await searchSimklId(title_id=aa['myAnimeList'], platform='mal')
                else:
                    simId = 0
            except:
                simId = 0

        rels = ""
        # Get the relations
        if (aa['aniDb'] is not None) and (pf != 'anidb'):
            rels += f"""\n<:aniDb:1073439145067806801> **AniDB**: [`{aa['aniDb']}`](<https://anidb.net/anime/{aa['aniDb']}>)"""
        if (aa['aniList'] is not None) and (pf != 'anilist'):
            rels += f"""\n<:aniList:1073445700689465374> **AniList**: [`{aa['aniList']}`](<https://anilist.co/anime/{aa['aniList']}>)"""
        if (aa['animePlanet'] is not None) and (pf != 'animeplanet'):
            rels += f"""\n<:animePlanet:1073446927447891998> **Anime-Planet**: [`{aa['animePlanet']}`](<https://www.anime-planet.com/anime/{aa['animePlanet']}>)"""
        if (aa['aniSearch'] is not None) and (pf != 'anisearch'):
            rels += f"""\n<:aniSearch:1073439148100300810> **aniSearch**: [`{aa['aniSearch']}`](<https://anisearch.com/anime/{aa['aniSearch']}>)"""
        if (aa['kaize'] is not None) and (pf != 'kaize'):
            rels += f"""\n<:kaize:1073441859910774784> **Kaize** (BETA, link may not working as expected): [`{aa['kaize']}`](<https://kaize.io/anime/{aa['kaize']}>)"""
        if (aa['kitsu'] is not None) and (pf != 'kitsu'):
            rels += f"""\n<:kitsu:1073439152462368950> **Kitsu**: [`{aa['kitsu']}`](<https://kitsu.io/anime/{aa['kitsu']}>)"""
        if (aa['liveChart'] is not None) and (pf != 'livechart'):
            rels += f"""\n<:liveChart:1073439158883844106> **LiveChart**: [`{aa['liveChart']}`](<https://livechart.me/anime/{aa['liveChart']}>)"""
        if (aa['myAnimeList'] is not None) and (platform != 'myanimelist'):
            rels += f"""\n<:myAnimeList:1073442204921643048> **MyAnimeList**: [`{aa['myAnimeList']}`](<https://myanimelist.net/anime/{aa['myAnimeList']}>)"""
        if (aa['notifyMoe'] is not None) and (pf != 'notify'):
            rels += f"""\n<:notifyMoe:1073439161194905690> **Notify**: [`{aa['notifyMoe']}`](<https://notify.moe/anime/{aa['notifyMoe']}>)"""
        if (aa['myAnimeList'] is not None) and (platform != 'shikimori'):
            rels += f"""\n<:shikimori:1073441855645155468> **Shikimori (Шикимори)**: [`{aa['myAnimeList']}`](<https://shikimori.one/animes/{aa['myAnimeList']}>)"""
        if (simId != 0) and (platform != 'simkl'):
            rels += f"""\n<:simkl:1073630754275348631> **SIMKL**: [`{simId}`](<https://simkl.com/anime/{simId}>)"""

        if pf == 'anidb':
            uid = f"https://anidb.net/anime/{id}"
            pf = 'AniDB'
        elif pf == 'anilist':
            uid = f"https://anilist.co/anime/{id}"
            pf = 'AniList'
        elif pf == 'animeplanet':
            uid = f"https://www.anime-planet.com/anime/{id}"
            pf = 'Anime-Planet'
        elif pf == 'anisearch':
            uid = f"https://anisearch.com/anime/{id}"
            pf = 'aniSearch'
        elif pf == 'kaize':
            uid = f"https://kaize.io/anime/{id}"
            pf = 'Kaize'
        elif pf == 'kitsu':
            uid = f"https://kitsu.io/anime/{id}"
            pf = 'Kitsu'
        elif platform == 'myanimelist':
            uid = f"https://myanimelist.net/anime/{id}"
            pf = 'MyAnimeList'
        elif platform == 'shikimori':
            uid = f"https://shikimori.one/animes/{id}"
            pf = 'Shikimori (Шикимори)'
        elif pf == 'livechart':
            uid = f"https://livechart.me/anime/{id}"
            pf = 'LiveChart'
        elif pf == 'notify':
            uid = f"https://notify.moe/anime/{id}"
            pf = 'Notify.moe'
        elif platform == 'simkl':
            uid = f"https://simkl.com/anime/{id}"
            pf = 'SIMKL'

        # generate the message
        sendMessages = f"""**{title}** relations to [{pf}](<{uid}>):\n{rels}"""
        sendMessages += f"""\n\n**Powered by [nattadasu's AnimeAPI](<https://nttds.my.id/discord>) and [SIMKL](<https://simkl.com>)**"""
        await ctx.edit(sendMessages)
    except Exception as e:
        if e == 'Expecting value: line 1 column 1 (char 0)':
            e = 'No relations found!\nEither the anime is not in the database, or you have entered the wrong ID.'
        else:
            e = e
        e = f"""While getting the relations for `{platform}` with id `{id}`, we got error message: {e}"""
        sendMessages = returnException(e)

        await ctx.edit(sendMessages)


@bot.command(
    name="random_nekomimi",
    description="Get a random image of characters with cat ears, powered by Natsu's nekomimiDb!"
)
async def random_nekomimi(ctx: interactions.CommandContext):
    pass


@random_nekomimi.subcommand()
async def bois(ctx: interactions.CommandContext):
    """Get a random image of male character with cat ears!"""
    await ctx.defer()
    row = await getNekomimi('boy')
    # get the image url
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=0x326799,
        author=interactions.EmbedAuthor(
            name="Powered by Natsu's nekomimiDb",
            url="https://github.com/nattadasu/nekomimiDb"
        ),
        fields=[
            interactions.EmbedField(
                name="Image source",
                value=f"[Click here]({imageSourceUrl})",
                inline=True
            ),
            interactions.EmbedField(
                name="Artist",
                value=f"[{artist}]({artistUrl})",
                inline=True
            )
        ]
    )
    await ctx.send("", embeds=dcEm)


@random_nekomimi.subcommand()
async def gurls(ctx: interactions.CommandContext):
    """Get a random image of female character with cat ears!"""
    await ctx.defer()
    row = await getNekomimi('girl')
    # get the image url
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=0x326799,
        author=interactions.EmbedAuthor(
            name="Powered by Natsu's nekomimiDb",
            url="https://github.com/nattadasu/nekomimiDb"
        ),
        fields=[
            interactions.EmbedField(
                name="Image source",
                value=f"[Click here]({imageSourceUrl})",
                inline=True
            ),
            interactions.EmbedField(
                name="Artist",
                value=f"[{artist}]({artistUrl})",
                inline=True
            )
        ]
    )
    await ctx.send("", embeds=dcEm)


@random_nekomimi.subcommand()
async def true_random(ctx: interactions.CommandContext):
    """Get a random image of characters with cat ears, whatever the gender they are!"""
    await ctx.defer()
    row = await getNekomimi()
    # get the image url
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=0x326799,
        author=interactions.EmbedAuthor(
            name="Powered by Natsu's nekomimiDb",
            url="https://github.com/nattadasu/nekomimiDb"
        ),
        fields=[
            interactions.EmbedField(
                name="Image source",
                value=f"[Click here]({imageSourceUrl})",
                inline=True
            ),
            interactions.EmbedField(
                name="Artist",
                value=f"[{artist}]({artistUrl})",
                inline=True
            )
        ]
    )
    await ctx.send("", embeds=dcEm)


@bot.command(
    name="manga",
    description="Get information about a manga, powered by AniList!"
)
async def manga(ctx: interactions.CommandContext):
    pass


@manga.subcommand(
    name="search",
    description="Search for a manga!",
    options=[
        interactions.Option(
            name="title",
            description="The title of the manga you want to search for",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def search(ctx: interactions.CommandContext, title: str):
    """Search for a manga!"""
    await ctx.defer()
    await ctx.get_channel()
    # get the manga
    try:
        rawData = await searchAniList(name=title, media_id=None, isAnime=False)
        bypass = await bypassAniListEcchiTag(alm=rawData[0])
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        dcEm = await generateAnilist(alm=rawData[0], isNsfw=nsfw_bool, bypassEcchi=bypass)
        sendMessages = None
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None

    await ctx.send(sendMessages, embeds=dcEm)


@manga.subcommand(
    options=[
        interactions.Option(
            name="id",
            description="The manga ID on AniList to fetch",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def info(ctx: interactions.CommandContext, id: int):
    """Get manga information from AniList using AniList id"""
    await ctx.defer()
    await ctx.get_channel()
    # get the manga
    try:
        rawData = await searchAniList(name=None, media_id=id, isAnime=False)
        bypass = await bypassAniListEcchiTag(alm=rawData[0])
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        dcEm = await generateAnilist(alm=rawData[0], isNsfw=nsfw_bool, bypassEcchi=bypass)
        sendMessages = None
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None

    await ctx.send(sendMessages, embeds=dcEm)


@bot.command(
    name="invite",
    description="Invite me to your server!"
)
async def invite(ctx: interactions.CommandContext):
    invLink = f"https://discord.com/api/oauth2/authorize?client_id={BOT_CLIENT_ID}&permissions=8&scope=bot%20applications.commands"
    dcEm = interactions.Embed(
        title=f"{EMOJI_ATTENTIVE} Thanks for your interest in inviting me to your server!",
        color=0x996422,
        description="To invite me, simply press \"**Invite me!**\" button below!\nFor any questions, please join my support server!",
        fields=[
            interactions.EmbedField(
                name="Required permissions/access",
                value="`Administrator`, for granting roles, kick/ban member",
                inline=True
            ),
            interactions.EmbedField(
                name="Required scopes",
                value="`bot`\n`applications.commands`",
                inline=True
            )
        ]
    )
    invBotton = interactions.Button(
        type=interactions.ComponentType.BUTTON,
        style=interactions.ButtonStyle.LINK,
        label="Invite me!",
        url=invLink
    )
    servBotton = interactions.Button(
        type=interactions.ComponentType.BUTTON,
        style=interactions.ButtonStyle.LINK,
        label="Support server",
        url=BOT_SUPPORT_SERVER
    )
    await ctx.send(embeds=dcEm, components=[invBotton, servBotton])


@bot.command(
    name="support",
    description="Give support to the bot!"
)
async def support(ctx: interactions.CommandContext):
    sendMessages = f"""{EMOJI_ATTENTIVE} Thanks for your interest in supporting me!

You can support me on [Ko-Fi](<https://ko-fi.com/nattadasu>), [PayPal](<https://paypal.me/nattadasu>), or [GitHub Sponsors](<https://github.com/sponsors/nattadasu>).

For Indonesian users, you can use [Trakteer](<https://trakteer.id/nattadasu>) or [Saweria](<https://saweria.co/nattadasu>).

Or, are you a developer? You can contribute to the bot's code on [GitHub](<https://github.com/nattadasu/ryuuRyuusei>)

If you have any questions (or more payment channels), please join my [support server]({BOT_SUPPORT_SERVER})!"""

    await ctx.send(sendMessages)


@bot.command(
    name="lastfm",
    description="Show Last.FM information about user!",
    options=[
        interactions.Option(
            name="username",
            description="User to lookup",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="maximum",
            description="Maximum scrobbled tracks to show",
            type=interactions.OptionType.INTEGER,
            min_value=0,
            max_value=9,
            required=False
        )
    ]
)
async def lastfm(ctx: interactions.CommandContext, username: str, maximum: int = 9):
    await ctx.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={username}&api_key={LASTFM_API_KEY}&format=json') as resp:
                if resp.status == 404:
                    raise Exception(
                        "User can not be found on Last.fm. Check the name or register?")
                else:
                    jsonText = await resp.text()
                    jsonFinal = jload(jsonText)
                    ud = jsonFinal['user']
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={LASTFM_API_KEY}&format=json&limit=9') as resp:
                jsonText = await resp.text()
                jsonFinal = jload(jsonText)
                scb = jsonFinal['recenttracks']['track']
        tracks = []
        # trim scb if items more than {maximum}
        if maximum > 0:
            if maximum > 1:
                rpt = "\n\n**Recently played tracks**"
            else:
                rpt = "\n\n**Recently played track**"
            if len(scb) > maximum:
                scb = scb[:maximum]
            for tr in scb:
                try:
                    if tr['@attr']['nowplaying'] is not None:
                        np = jload(tr['@attr']['nowplaying'].lower())
                except:
                    np = False
                # sanitize title to be markdown compatible
                tr['name'] = str(tr['name']).replace("*", "\\*").replace("_", "\\_").replace("`", "\\`").replace("~", "\\~").replace("|", "\\|").replace(
                    ">", "\\>").replace("<", "\\<").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("/", "\\/")
                tr['artist']['#text'] = str(tr['artist']['#text']).replace("*", "\\*").replace("_", "\\_").replace("`", "\\`").replace("~", "\\~").replace(
                    "|", "\\|").replace(">", "\\>").replace("<", "\\<").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("/", "\\/")
                tr['album']['#text'] = str(tr['album']['#text']).replace("*", "\\*").replace("_", "\\_").replace("`", "\\`").replace("~", "\\~").replace(
                    "|", "\\|").replace(">", "\\>").replace("<", "\\<").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("/", "\\/")
                if np is True:
                    title = f"▶️ {tr['name']}"
                    dt = "*Currently playing*"
                else:
                    title = tr['name']
                    dt = int(tr['date']['uts'])
                    dt = f"<t:{dt}:R>"
                tracks += [interactions.EmbedField(
                    name=title,
                    value=f"""{tr['artist']['#text']}
{tr['album']['#text']}
{dt}, [Link]({tr['url']})""",
                    inline=True
                )]
        else:
            rpt = ""
        # read ud['images'], and grab latest one
        imgLen = len(ud['image'])
        img = ud['image'][imgLen - 1]['#text']
        lfmpro = ud['subscriber']
        icShine = "<:icons_shine1:859424400959602718>"
        if lfmpro == "1":
            lfmpro = f"{icShine} Last.FM Pro User\n"
            badge = icShine + " "
        else:
            lfmpro, badge = "", ""
        # building embed
        dcEm = interactions.Embed(
            author=interactions.EmbedAuthor(
                name="Last.FM Profile",
                url="https://last.fm",
                icon_url="https://media.discordapp.net/attachments/923830321433149453/1079483003396432012/Tx1ceVTBn2Xwo2dF.png"
            ),
            title=f"{badge}{ud['name']}'s Last.FM Profile",
            url=ud['url'],
            color=0xF71414,
            description=f"""{lfmpro}Real name: {ud['realname']}
Account created: <t:{ud['registered']['#text']}:D> (<t:{ud['registered']['#text']}:R>)
Total scrobbles: {ud['playcount']}
🧑‍🎤 {ud['artist_count']}  💿 {ud['album_count']} 🎶 {ud['track_count']}{rpt}""",
            thumbnail=interactions.EmbedImageStruct(
                url=img
            ),
            fields=tracks
        )
        sendMessages = None
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None

    await ctx.send(sendMessages, embeds=dcEm)


@bot.command(
    name="admin_register",
    description="Register user to the bot, for admin only!",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="dc_username",
            description="The user to register",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.Option(
            name="mal_username",
            description="The user's MAL username",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def admin_register(ctx: interactions.CommandContext, dc_username: int, mal_username: str):
    await ctx.defer(ephemeral=True)
    discordId = dc_username.id
    discordUsername = dc_username.username
    discordDiscriminator = dc_username.discriminator
    discordJoined = int(snowflake_to_datetime(dc_username.id))
    discordServerName = ctx.guild.name
    malUname = mal_username.strip()
    try:
        if checkIfRegistered(discordId):
            sendMessages = f"""{EMOJI_DOUBTING} **User is already registered!**"""
        else:
            jikanData = await getJikanData(malUname)
            malUid = jikanData['mal_id']
            jikanData['joined'] = jikanData['joined'].replace(
                '+00:00', '+0000')
            malJoined = int(datetime.datetime.strptime(
                jikanData['joined'], "%Y-%m-%dT%H:%M:%S%z").timestamp())
            registeredAt = int(datetime.datetime.now().timestamp())
            registeredGuild = ctx.guild_id
            registeredBy = ctx.author.id
            sendMessages = f"""{EMOJI_SUCCESS} **User registered!**```json
{{
    "discordId": {discordId},
    "discordUsername": "{discordUsername}#{discordDiscriminator}",
    "discordJoined": {discordJoined},
    "registeredGuildId": {registeredGuild},
    "registeredGuildName": "{discordServerName}",
    "malUname": "{malUname}",
    "malId": {malUid},
    "malJoined": {malJoined},
    "registeredAt": {registeredAt},
    "registeredBy": {registeredBy} // it's you, {ctx.author.username}#{ctx.author.discriminator}!
}}```"""
            saveToDatabase(discordId, f'{discordUsername}#{discordDiscriminator}', discordJoined, str(
                malUname), malUid, malJoined, registeredAt, registeredGuild, registeredBy, discordServerName)
    except Exception as e:
        sendMessages = returnException(e)

    await ctx.send(sendMessages, ephemeral=True)


@bot.command(
    name="admin_unregister",
    description="Unregister user from the bot, for admin only!",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="dc_username",
            description="The user to unregister",
            type=interactions.OptionType.USER,
            required=True
        )
    ]
)
async def admin_unregister(ctx: interactions.CommandContext, dc_username: int):
    await ctx.defer(ephemeral=True)
    discordId = dc_username.id
    if checkIfRegistered(discordId):
        try:
            df = pd.read_csv(database, sep="\t")
            df_drop = df.drop(df.query(f'discordId == {discordId}').index)
            df_drop.to_csv(database, sep="\t", index=False, encoding="utf-8")
            sendMessages = f"""{EMOJI_SUCCESS} **User unregistered!**"""
        except Exception as e:
            sendMessages = returnException(e)
    else:
        sendMessages = f"""{EMOJI_DOUBTING} **User is not registered!**"""

    await ctx.send(sendMessages, ephemeral=True)


print("Starting bot...")

bot.start()
