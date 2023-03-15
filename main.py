#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cspell:disable

import csv
import datetime
import html
import json
import os
import subprocess
import time
from json import loads as jload
from urllib.parse import quote as urlquote
from uuid import uuid4 as id4
from zoneinfo import ZoneInfo

import aiohttp
import html5lib
import interactions
import pandas as pd
import regex as re
from bs4 import BeautifulSoup
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
TRAKT_CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
TRAKT_API_VERSION = os.getenv('TRAKT_API_VERSION')

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


# https://stackoverflow.com/a/21901260
def get_git_revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()


def get_git_revision_short_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


gittyHash = get_git_revision_hash()
gtHsh = get_git_revision_short_hash()


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
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://aniapi.nattadasu.my.id/{platform}/{id}') as resp:
                jsonText = await resp.text()
                jsonFinal = jload(jsonText)
            await session.close()
            return jsonFinal
    except:
        aaDict = {
            'title': None,
            'aniDb': None,
            'aniList': None,
            'animePlanet': None,
            'aniSearch': None,
            'kaize': None,
            'kitsu': None,
            'liveChart': None,
            'myAnimeList': None,
            'notifyMoe': None,
            'silverYasha': None
        }
        return aaDict


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


async def searchSimklId(title_id: str, platform: str):
    url = f'https://api.simkl.com/search/id/?{platform}={title_id}&client_id={SIMKL_CLIENT_ID}'
    try:
        async with aiohttp.ClientSession() as sSession:
            async with sSession.get(url) as sResp:
                idFound = await sResp.json()
                fin = idFound[0]['ids']['simkl']
            await sSession.close()
            return fin
    except:
        return 0


simkl0rels = {
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
    "fanart": None,
    "anitype": None,
    'title': None
}


async def getSimklID(simkl_id: int, media_type: str) -> dict:
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
                        "fanart": animeFound.get('fanart', None),
                        "aniType": animeFound.get('anime_type', None),
                        "title": animeFound.get('title', None)
                    }
                await gSession.close()
                return data
    except:
        return simkl0rels


def trimCyno(message: str):
    if len(message) > 1000:
        msg = message[:1000]
        # trim spaces
        msg = msg.strip()
        return msg + "..."
    else:
        return message


def generateTrailer(data: dict, isMal: bool = False) -> interactions.Button:
    if isMal:
        ytid = data['youtube_id']
    else:
        ytid = data['id']
    final = interactions.Button(
        type=interactions.ComponentType.BUTTON,
        label="PV/CM on YouTube",
        style=interactions.ButtonStyle.LINK,
        url=f"https://www.youtube.com/watch?v={ytid}",
        emoji=interactions.Emoji(
            id=975564205228965918,
            name="Youtube"
        )
    )
    return final


async def generateMal(entry_id: int, isNsfw: bool = False, alDict: dict = None, animeApi: dict = None):
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
    aa = animeApi

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

    if (aa['kitsu'] is not None) and (((alPost is None) and (alBg is None)) or ((smkPost is None) and (smkBg is None))):
        kts = await getKitsuMetadata(aa['kitsu'], 'anime')
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

        if len(str(cynoin)) <= 150:
            cyno = cynoin
            if cynl >= 3:
                cyno += "\n> \n> "
                cyno += trimCyno(cyno[2])
        elif len(str(cynoin)) >= 1000:
            cyno = trimCyno(cynoin)
        else:
            cyno = cynoin

        if (cyno[-3:] == "...") or ((len(str(cynoin)) >= 150) and (cynl > 3)) or ((len(str(cynoin)) >= 1000) and (cynl > 1)):
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
        tgss = sorted(set(tgs[:20]))
        tgs = ", ".join(tgss)
        tgs += f", *and {len(tgss) - 20} more*"
    else:
        tgss = sorted(set(tgs))
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


def getRandom(value: int = 9) -> int:
    seed = id4()
    # negate value
    value = -value
    seed = int(str(seed.int)[value:])
    return seed


async def getNekomimi(gender: str = None):
    seed = getRandom()
    nmDb = pd.read_csv("database/nekomimiDb.tsv", sep="\t")
    nmDb = nmDb.fillna('')
    if gender is not None:
        query = nmDb[nmDb['girlOrBoy'] == f'{gender}']
    else:
        query = nmDb
    # get a random row from the query
    row = query.sample(n=1, random_state=seed)
    return row


def getPlatformColor(pf: str) -> hex:
    pf = pf.lower()
    if pf == "twitter":
        cl = 0x15202B
    elif pf == "pixiv":
        cl = 0x0096FA
    elif pf == "deviantart":
        cl = 0x05CC47
    elif pf == "instagram":
        cl = 0x833AB4
    elif pf == "tumblr":
        cl = 0x35465C
    elif pf == "patreon":
        cl = 0xF96854
    elif pf == "artstation":
        cl = 0x0F0F0F
    elif pf == "lofter":
        cl = 0x335F60
    elif pf == "weibo":
        cl = 0xE6162D
    elif pf == "seiga":
        cl = 0xEDA715
    elif pf == "reddit":
        cl = 0xFF4500
    elif pf == "hoyolab":
        cl = 0x1B75BB
    elif pf == 'anidb':
        cl = 0x2A2F46
    elif pf == 'anilist':
        cl = 0x2F80ED
    elif pf == 'animeplanet':
        cl = 0xE75448
    elif pf == 'anisearch':
        cl = 0xFDA37C
    elif pf == 'kaize':
        cl = 0x692FC2
    elif pf == 'kitsu':
        cl = 0xF85235
    elif pf == 'myanimelist':
        cl = 0x2F51A3
    elif pf == 'shikimori':
        cl = 0x2E2E2E
    elif pf == 'livechart':
        cl = 0x67A427
    elif pf == 'notify':
        cl = 0xDEA99E
    elif pf == 'simkl':
        cl = 0x0B0F10
    elif pf == 'tvdb':
        cl = 0x6CD491
    elif pf == 'tmdb':
        cl = 0x09B4E2
    elif pf == 'imdb':
        cl = 0xF5C518
    elif pf == 'silveryasha':
        cl = 0x0172BB
    return cl


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
                    await ctx.member.add_role(verifiedRole, reason="Verified by bot")
                    messages = f"""{EMOJI_ATTENTIVE} **You have been verified!**"""
                    verified = True
                    # exit the loop
                    break
            if verified is False:
                messages = f"""{EMOJI_USER_ERROR} **You are not in the club!**
Please join [our club](<https://myanimelist.net/clubs.php?cid={CLUB_ID}>) to get your role!"""
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

    def generate_embed(uname: str, uid: int, malAnime: dict, malManga: dict, joined: int, bday: int = None, extend: bool = False) -> interactions.Embed:
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
Account created: <t:{joined}:D> (<t:{joined}:R>){bbd}""",
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
                                bth = malProfile['birthday'].replace(
                                    "+00:00", "+0000")
                                bth = int(datetime.datetime.strptime(
                                    bth, "%Y-%m-%dT%H:%M:%S%z").timestamp())
                            dtJoin = malProfile['joined'].replace(
                                "+00:00", "+0000")
                            dtJoin = int(datetime.datetime.strptime(
                                dtJoin, "%Y-%m-%dT%H:%M:%S%z").timestamp())

                            dcEm = generate_embed(uname=mun, uid=mid, malAnime=ani, malManga=man,
                                                  joined=dtJoin, bday=bth, extend=extended)
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
                bth = int(datetime.datetime.strptime(
                    bth, "%Y-%m-%dT%H:%M:%S%z").timestamp())
            dtJoin = malProfile['joined'].replace("+00:00", "+0000")
            dtJoin = int(datetime.datetime.strptime(
                dtJoin, "%Y-%m-%dT%H:%M:%S%z").timestamp())

            dcEm = generate_embed(uname=mun, uid=mid, malAnime=ani, malManga=man,
                                  joined=dtJoin, bday=bth, extend=extended)
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

Bot version, in Git hash: [`{gtHsh}`](<https://github.com/nattadasu/ryuuRyuusei/commit/{gittyHash}>)
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

    ani_id = None
    alData = None

    async def lookupByNameAniList(aniname: str):
        rawData = await searchAniList(name=aniname, media_id=None, isAnime=True)
        return rawData

    async def lookupByNameJikan(name: str):
        rawData = await searchJikanAnime(name)
        for ani in rawData:
            romaji = ani['title']
            english = ani['title_english']
            native = ani['title_japanese']
            syns = ani['titles']
            if (romaji == name) or (english == name) or (native == name):
                return ani
            else:
                for title in syns:
                    if title == name:
                        return ani

    trailer = None

    try:
        await ctx.send(f"Searching `{title}` using AniList", embeds=None, components=None)
        alData = await lookupByNameAniList(title)
        ani_id = alData[0]['idMal']
        if (alData[0]['trailer'] is not None) and (alData[0]['trailer']['site'] == "youtube"):
            trailer = generateTrailer(data=alData[0]['trailer'], isMal=False)
    except:
        ani_id = None

    if ani_id is None:
        try:
            await ctx.edit(f"AniList failed to search `{title}`, searching via Jikan (inaccurate)", embeds=None, components=None)
            ani = await lookupByNameJikan(title)
            ani_id = ani['mal_id']
            if (ani['trailer'] is not None) and (ani['trailer']['youtube_id'] is not None):
                trailer = generateTrailer(data=ani['trailer'], isMal=True) 
        except:
            ani_id = None

    if ani_id is not None:
        try:
            await ctx.edit("Anime found! Processing", embeds=None)
            # check if command invoked in a forum thread
            if ctx.channel.type == 11 or ctx.channel.type == 12:
                # get parent channel id
                prId = ctx.channel.parent_id
                # get NSFW status
                nsfw_bool = await getParentNsfwStatus(snowflake=prId)
            else:
                nsfw_bool = ctx.channel.nsfw
            aniApi = await getNatsuAniApi(ani_id, platform="myanimelist")
            dcEm = await generateMal(ani_id, nsfw_bool, alDict=alData, animeApi=aniApi)
            sendMessages = None
        except Exception as e:
            sendMessages = returnException(e)
            dcEm = None
            trailer = None
    else:
        sendMessages = returnException(
            f"""We couldn't able to find any anime with that title (`{title}`). Please check the spelling!
**Pro tip**: Use Native title to get most accurate result.... that if you know how to type in such language.""")
        dcEm = None
        trailer = None

    await ctx.edit(sendMessages, embeds=dcEm, components=trailer)


@anime.subcommand()
async def random(ctx: interactions.CommandContext):
    """Get random anime information from MAL"""
    await ctx.defer()
    await ctx.get_channel()

    async def lookupRandom():
        seed = getRandom()
        # open database/mal.csv
        df = pd.read_csv("database/mal.csv", sep="\t")
        # get random anime
        randomAnime = df.sample(n=1, random_state=seed)
        # get anime id
        randomAnimeId: int = randomAnime['mal_id'].values[0]
        return randomAnimeId

    ani_id = await lookupRandom()
    trailer = None

    await ctx.send(f"Found [`{ani_id}`](<https://myanimelist.net/anime/{ani_id}>), showing information...", ephemeral=True)

    try:
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        sendMessages = None
        aniApi = await getNatsuAniApi(ani_id, platform="myanimelist")
        if aniApi['aniList'] is not None:
            aaDict = await searchAniList(media_id=aniApi['aniList'], isAnime=True)
            if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                trailer = generateTrailer(data=aaDict[0]['trailer'])
        else:
            try:
                aaDict = await searchAniList(name=aniApi['title'], media_id=None, isAnime=True)
                if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                    trailer = generateTrailer(data=aaDict[0]['trailer'])
            except:
                aaDict = None
        dcEm = await generateMal(ani_id, nsfw_bool, aaDict, animeApi=aniApi)
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None
        trailer = None

    await ctx.send(sendMessages, embeds=dcEm, components=trailer)


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
    trailer = None
    try:
        # check if command invoked in a forum thread
        if ctx.channel.type == 11 or ctx.channel.type == 12:
            # get parent channel id
            prId = ctx.channel.parent_id
            # get NSFW status
            nsfw_bool = await getParentNsfwStatus(snowflake=prId)
        else:
            nsfw_bool = ctx.channel.nsfw
        aniApi = await getNatsuAniApi(id=id, platform='myanimelist')
        if aniApi['aniList'] is not None:
            aaDict = await searchAniList(media_id=aniApi['aniList'], isAnime=True)
            if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                trailer = generateTrailer(data=aaDict[0]['trailer'])
        else:
            try:
                aaDict = await searchAniList(name=aniApi['title'], media_id=None, isAnime=True)
                if (aaDict[0]['trailer'] is not None) and (aaDict[0]['trailer']['site'] == "youtube"):
                    trailer = generateTrailer(data=aaDict[0]['trailer'])
            except:
                aaDict = None
        dcEm = await generateMal(id, nsfw_bool, aaDict, animeApi=aniApi)
        sendMessages = None
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None
        trailer = None

    await ctx.send(sendMessages, embeds=dcEm, components=trailer)


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
                    name="IMDb",
                    value="imdb"
                ),
                interactions.Choice(
                    name="Kaize (BETA, slug only)",
                    value="kaize"
                ),
                interactions.Choice(
                    name="Kitsu",
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
                    name="Silver Yasha: DB Tontonan Indonesia",
                    value="silveryasha"
                ),
                interactions.Choice(
                    name="SIMKL",
                    value="simkl"
                ),
                interactions.Choice(
                    name="The Movie Database",
                    value="tmdb"
                ),
                interactions.Choice(
                    name="The TVDB",
                    value="tvdb"
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
        simId = 0
        await ctx.send(f"Searching for relations on `{platform}` using ID: `{uid}`", embeds=None)
        # Fix platform name
        if platform == 'shikimori':
            pf = 'myanimelist'
            # remove any prefix started with any a-z in the id
            uid = re.sub(r'^[a-z]+', '', id)
            await ctx.edit("Removing Shikimori ID's prefix to be compatible with MyAnimeList ID", embeds=None)

        if pf == 'simkl':
            simDat = await getSimklID(simkl_id=id, media_type='anime')
            simId = id
            # if simDat['mal'] key is not in the dict, it will raise KeyError
            try:
                uid = simDat['mal']
                pf = 'myanimelist'
            except KeyError:
                raise Exception(
                    "No MAL ID found, please ask the SIMKL developer to add it to the database")
        elif pf in ['tmdb', 'tvdb', 'imdb']:
            try:
                simId = await searchSimklId(title_id=id, platform=pf)
                simDat = await getSimklID(simkl_id=simId, media_type='anime')
                uid = simDat['mal']
                pf = 'myanimelist'
            except KeyError:
                raise Exception(
                    f"Error while searching for the ID of `{platform}` on SIMKL, entry may not linked with SIMKL counterpart")

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
                    await ctx.edit(f"Searching for relations on `{platform}` using ID: `{uid}` (decrease by one)", embeds=None)
                    aa = await getNatsuAniApi(id=uid, platform=pf)
            except json.JSONDecodeError:
                raise Exception("""We've tried to search for the anime using the slug (and even fix the slug itself), but it seems that the anime is not found on Kaize via AnimeApi.
Please send a message to AnimeApi maintainer, nattadasu (he is also a developer of this bot)""")
        elif pf == 'kitsu':
            # check if the ID provided is a slug
            if re.match(r'^[a-z0-9-]+$', uid):
                # get the anime ID
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://kitsu.io/api/edge/anime?filter[slug]={uid}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            uid = data['data'][0]['id']
                        else:
                            raise Exception(
                                "Error while searching for the ID of Kitsu")
                    await session.close()
                await ctx.edit(f"Searching for relations on `{platform}` using ID: `{uid}` (slug to ID)", embeds=None)
            else:
                uid = int(uid)
            aa = await getNatsuAniApi(id=uid, platform=pf)
        else:
            aa = await getNatsuAniApi(id=uid, platform=pf)

        # Get the anime title
        title = aa['title']

        smk = simkl0rels

        # Get the relations from others to SIMKL, if MAL is found
        if platform not in ['simkl', 'tmdb', 'tvdb', 'imdb']:
            try:
                if aa['myAnimeList'] is not None:
                    # search SIMKL ID
                    simId = await searchSimklId(title_id=aa['myAnimeList'], platform='mal')
                    # get the relations
                    smk = await getSimklID(simkl_id=simId, media_type='anime')
            except:
                pass
        elif platform == 'simkl':
            try:
                smk = await getSimklID(simkl_id=simId, media_type='anime')
            except:
                pass
        else:
            smk = simDat

        if (title is None) and (simId != 0):
            title = smk['title']

        traktId = 0

        if smk['imdb'] is not None:
            # well, IMDb is basically de-facto for TV/Movie database
            # similar to MyAnimeList
            tid = smk['imdb']
            lookup = f"imdb/{tid}"
            scpf = "IMDb"
            try:
                async with aiohttp.ClientSession(headers={
                    'Content-Type': 'applications/json',
                    'trakt-api-key': TRAKT_CLIENT_ID,
                    'trakt-api-version': TRAKT_API_VERSION
                }) as session:
                    async with session.get(f'https://api.trakt.tv/search/{lookup}') as resp:
                        await ctx.edit(f"Looking up Trakt ID via {scpf} (`{tid}`)", embeds=None)
                        trkRes = await resp.json()
                        trkType = trkRes[0]['type']
                        traktId = int(trkRes[0][f'{trkType}']['ids']['trakt'])
                    await session.close()
            except:
                traktId = 0

        relsEm = []
        # Get the relations
        if smk['allcin'] is not None:
            relsEm += [interactions.EmbedField(
                name="<:allcinema:1079493870326403123> AllCinema",
                value=f"[`{smk['allcin']}`](<https://www.allcinema.net/prog/show_c.php?num_c={smk['allcin']}>)",
                inline=True
            )]
        if (aa['aniDb'] is not None) and (pf != 'anidb'):
            relsEm += [interactions.EmbedField(
                name="<:aniDb:1073439145067806801> AniDB",
                value=f"[`{aa['aniDb']}`](<https://anidb.net/anime/{aa['aniDb']}>)",
                inline=True
            )]
        if (aa['aniList'] is not None) and (pf != 'anilist'):
            relsEm += [interactions.EmbedField(
                name="<:aniList:1073445700689465374> AniList",
                value=f"[`{aa['aniList']}`](<https://anilist.co/anime/{aa['aniList']}>)",
                inline=True
            )]
        if smk['ann'] is not None:
            relsEm += [interactions.EmbedField(
                name="<:ann:1079377192951230534> Anime News Network",
                value=f"[`{smk['ann']}`](<https://www.animenewsnetwork.com/encyclopedia/anime.php?id={smk['ann']}>)",
                inline=True
            )]
        if (aa['animePlanet'] is not None) and (pf != 'animeplanet'):
            relsEm += [interactions.EmbedField(
                name="<:animePlanet:1073446927447891998> Anime-Planet",
                value=f"[`{aa['animePlanet']}`](<https://www.anime-planet.com/anime/{aa['animePlanet']}>)",
                inline=True
            )]
        if (aa['aniSearch'] is not None) and (pf != 'anisearch'):
            relsEm += [interactions.EmbedField(
                name="<:aniSearch:1073439148100300810> aniSearch",
                value=f"[`{aa['aniSearch']}`](<https://anisearch.com/anime/{aa['aniSearch']}>)",
                inline=True
            )]
        if (smk['imdb'] is not None) and (platform != "imdb"):
            relsEm += [interactions.EmbedField(
                name="<:IMDb:1079376998880784464> IMDb",
                value=f"[`{smk['imdb']}`](<https://www.imdb.com/title/{smk['imdb']}>)",
                inline=True
            )]
        if (aa['kaize'] is not None) and (pf != 'kaize'):
            relsEm += [interactions.EmbedField(
                name="<:kaize:1073441859910774784> Kaize",
                value=f"(BETA, link may not working as expected)\n[`{aa['kaize']}`](<https://kaize.io/anime/{aa['kaize']}>)",
                inline=True
            )]
        if (aa['kitsu'] is not None) and (pf != 'kitsu'):
            relsEm += [interactions.EmbedField(
                name="<:kitsu:1073439152462368950> Kitsu",
                value=f"[`{aa['kitsu']}`](<https://kitsu.io/anime/{aa['kitsu']}>)",
                inline=True
            )]
        if (aa['liveChart'] is not None) and (pf != 'livechart'):
            relsEm += [interactions.EmbedField(
                name="<:liveChart:1073439158883844106> LiveChart",
                value=f"[`{aa['liveChart']}`](<https://livechart.me/anime/{aa['liveChart']}>)",
                inline=True
            )]
        if (aa['myAnimeList'] is not None) and (platform != 'myanimelist'):
            relsEm += [interactions.EmbedField(
                name="<:myAnimeList:1073442204921643048> MyAnimeList",
                value=f"[`{aa['myAnimeList']}`](<https://myanimelist.net/anime/{aa['myAnimeList']}>)",
                inline=True
            )]
        if (aa['notifyMoe'] is not None) and (pf != 'notify'):
            relsEm += [interactions.EmbedField(
                name="<:notifyMoe:1073439161194905690> Notify",
                value=f"[`{aa['notifyMoe']}`](<https://notify.moe/anime/{aa['notifyMoe']}>)",
                inline=True
            )]
        if (aa['myAnimeList'] is not None) and (platform != 'shikimori'):
            relsEm += [interactions.EmbedField(
                name="<:shikimori:1073441855645155468> Shikimori (Шикимори)",
                value=f"[`{aa['myAnimeList']}`](<https://shikimori.one/animes/{aa['myAnimeList']}>)",
                inline=True
            )]
        if (aa['silverYasha'] is not None) and (platform != 'silveryasha'):
            relsEm += [interactions.EmbedField(
                name="<:silverYasha:1079380182059733052> Silver Yasha",
                value=f"[`{aa['silverYasha']}`](<https://db.silveryasha.web.id/anime/{aa['silverYasha']}>)",
                inline=True
            )]
        if (simId != 0) and (platform != 'simkl'):
            relsEm += [interactions.EmbedField(
                name="<:simkl:1073630754275348631> SIMKL",
                value=f"[`{simId}`](<https://simkl.com/anime/{simId}>)",
                inline=True
            )]
        if (traktId != 0) and (platform != "trakt"):
            relsEm += [interactions.EmbedField(
                name=f"<:trakt:1081612822175305788> Trakt",
                value=f"[`{traktId}`](<https://trakt.tv/{trkType}/{traktId}>)",
                inline=True
            )]
        try:
            if traktId != 0:
                if trkType == "show":
                    tvtyp = "series"
                    tmtyp = "tv"
                else:
                    tvtyp = "movies"
                    tmtyp = "movie"
            else:
                if smk['aniType'] == "tv":
                    tvtyp = "series"
                    tmtyp = "tv"
                elif smk['aniType'] is not None:
                    tvtyp = "movies"
                    tmtyp = "movie"
        except:
            tvtyp = "series"
            tmtyp = "tv"
        if (smk['tmdb'] is not None) and (platform != "tmdb"):
            relsEm += [interactions.EmbedField(
                name="<:tmdb:1079379319920529418> The Movie Database",
                value=f"[`{smk['tmdb']}`](<https://www.themoviedb.org/{tmtyp}/{smk['tmdb']}>)",
                inline=True
            )]
        if (smk['tvdb'] is not None) and (platform != "tvdb"):
            relsEm += [interactions.EmbedField(
                name="<:tvdb:1079378495064510504> The TVDB",
                value=f"[`{smk['tvdb']}`](<https://www.thetvdb.com/?tab={tvtyp}&id={smk['tvdb']}>)",
                inline=True
            )]
        elif (smk['tvdbslug'] is not None) and (platform != "tvdb"):
            relsEm += [interactions.EmbedField(
                name="<:tvdb:1079378495064510504> The TVDB",
                value=f"[`{smk['tvdbslug']}`](<https://www.thetvdb.com/{tvtyp}/{smk['tvdbslug']}>)",
                inline=True
            )]

        col = getPlatformColor(platform)

        if pf == 'anidb':
            uid = f"https://anidb.net/anime/{id}"
            pf = 'AniDB'
            emoid = '1073439145067806801'
        elif pf == 'anilist':
            uid = f"https://anilist.co/anime/{id}"
            pf = 'AniList'
            emoid = '1073445700689465374'
        elif pf == 'animeplanet':
            uid = f"https://www.anime-planet.com/anime/{id}"
            pf = 'Anime-Planet'
            emoid = '1073446927447891998'
        elif pf == 'anisearch':
            uid = f"https://anisearch.com/anime/{id}"
            pf = 'aniSearch'
            emoid = '1073439148100300810'
        elif pf == 'kaize':
            uid = f"https://kaize.io/anime/{id}"
            pf = 'Kaize'
            emoid = '1073441859910774784'
        elif pf == 'kitsu':
            uid = f"https://kitsu.io/anime/{id}"
            pf = 'Kitsu'
            emoid = '1073439152462368950'
        elif platform == 'myanimelist':
            uid = f"https://myanimelist.net/anime/{id}"
            pf = 'MyAnimeList'
            emoid = '1073442204921643048'
        elif platform == 'shikimori':
            uid = f"https://shikimori.one/animes/{id}"
            pf = 'Shikimori (Шикимори)'
            emoid = '1073441855645155468'
        elif pf == 'livechart':
            uid = f"https://livechart.me/anime/{id}"
            pf = 'LiveChart'
            emoid = '1073439158883844106'
        elif pf == 'notify':
            uid = f"https://notify.moe/anime/{id}"
            pf = 'Notify.moe'
            emoid = '1073439161194905690'
        elif platform == 'simkl':
            uid = f"https://simkl.com/anime/{id}"
            pf = 'SIMKL'
            emoid = '1073630754275348631'
        elif (platform == 'tvdb') and (smk['tvdb'] is not None):
            uid = f"https://www.thetvdb.com/?tab={tvtyp}&id={id}"
            pf = 'The TV Database'
            emoid = '1079378495064510504'
        elif (platform == 'tvdb') and (smk['tvdbslug'] is not None):
            uid = f"https://www.thetvdb.com/{tvtyp}/{id}"
            pf = 'The TV Database'
            emoid = '1079378495064510504'
        elif platform == 'tmdb':
            uid = f"https://www.themoviedb.org/{tmtyp}/{id}"
            pf = 'The Movie Database'
            emoid = '1079379319920529418'
        elif platform == 'imdb':
            uid = f"https://www.imdb.com/title/{id}"
            pf = 'IMDb'
            emoid = '1079376998880784464'
        elif pf == 'silveryasha':
            uid = f"<https://db.silveryasha.web.id/anime/{id}>"
            pf = "Silver Yasha"
            emoid = "1079380182059733052"

        if (smk['poster'] is None) and (aa['kitsu'] is not None):
            poster = f"https://media.kitsu.io/anime/poster_images/{aa['kitsu']}/large.jpg"
            postsrc = "Kitsu"
        elif (smk['poster'] is None) and (aa['notifyMoe'] is not None):
            poster = f"https://media.notify.moe/images/anime/original/{aa['notifyMoe']}.jpg"
            postsrc = "Notify.moe"
        elif smk['poster'] is not None:
            poster = f"https://simkl.in/posters/{smk['poster']}_m.webp"
            postsrc = "SIMKL"
        else:
            poster = None
            postsrc = None

        if postsrc is not None:
            postsrc = f" Poster from {postsrc}"
        else:
            postsrc = ""

        uAu = uid.split('/')
        uAu = uAu[0] + "//" + uAu[2]

        # generate the message
        dcEm = interactions.Embed(
            author=interactions.EmbedAuthor(
                name=f"Looking external site relations from {pf}",
                icon_url=f"https://cdn.discordapp.com/emojis/{emoid}.png?v=1",
                url=uAu
            ),
            title=f"{title}",
            url=uid,
            description="Data might be inaccurate, especially for sequels of the title (as IMDb, TVDB, TMDB, and Trakt relies on per title entry than season entry)",
            color=col,
            fields=relsEm,
            footer=interactions.EmbedFooter(
                text=f"Powered by nattadasu's AnimeAPI and SIMKL.{postsrc}"
            ),
            thumbnail=interactions.EmbedImageStruct(
                url=poster
            )
        )
        await ctx.edit("", embeds=dcEm)
    except Exception as e:
        if e == 'Expecting value: line 1 column 1 (char 0)':
            e = 'No relations found!\nEither the anime is not in the database, or you have entered the wrong ID.'
        else:
            e = e
        e = f"""While getting the relations for `{platform}` with id `{id}`, we got error message: {e}"""
        sendMessages = returnException(e)

        await ctx.edit(sendMessages, embeds=None)


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
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=col,
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
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=col,
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
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=col,
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
    trailer = None
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
        if (rawData[0]['trailer'] is not None) and (rawData[0]['trailer']['site'] == "youtube"):
            trailer = generateTrailer(data=rawData[0]['trailer'])
        sendMessages = None
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None
        trailer = None

    await ctx.send(sendMessages, embeds=dcEm, components=trailer)


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
    trailer = None
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
        if (rawData[0]['trailer'] is not None) and (rawData[0]['trailer']['site'] == "youtube"):
            trailer = generateTrailer(data=rawData[0]['trailer'])
        sendMessages = None
    except Exception as e:
        sendMessages = returnException(e)
        dcEm = None
        trailer = None

    await ctx.send(sendMessages, embeds=dcEm, components=trailer)


@bot.command(
    name="invite",
    description="Invite me to your server!"
)
async def invite(ctx: interactions.CommandContext):
    invLink = f"https://discord.com/api/oauth2/authorize?client_id={BOT_CLIENT_ID}&permissions=274878221376&scope=bot%20applications.commands"
    dcEm = interactions.Embed(
        title=f"{EMOJI_ATTENTIVE} Thanks for your interest in inviting me to your server!",
        color=0x996422,
        description="To invite me, simply press \"**Invite me!**\" button below!\nFor any questions, please join my support server!",
        fields=[
            interactions.EmbedField(
                name="Required permissions/access",
                value="Read Messages, Send Messages, Send Messages in Thread, Embed Links, Attach Files, Use External Emojis, Add Reactions",
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
    await ctx.send(f"Fetching data for {username}...", embeds=None)
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
            await session.close()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={LASTFM_API_KEY}&format=json&limit=9') as resp:
                jsonText = await resp.text()
                jsonFinal = jload(jsonText)
                scb = jsonFinal['recenttracks']['track']
            await session.close()
        tracks = []
        # trim scb if items more than {maximum}
        if maximum > 0:
            if maximum > 1:
                rpt = "\n\n**Recently played tracks**"
            else:
                rpt = "\n\n**Recently played track**"
            if len(scb) > maximum:
                scb = scb[:maximum]
            nRep = 1
            for tr in scb:
                await ctx.edit(f"Fetching data for {username}... {nRep}/{maximum}", embeds=None)
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
                scu = tr['url']
                scus = scu.split("/")
                # assumes the url as such: https://www.last.fm/music/Artist/_/Track
                # so, the artist is at index 4, and track is at index 6
                # in index 4 and 6, encode the string to be url compatible with percent encoding
                track = []
                for art in scus[6].split("+"):
                    track.append(urlquote(art))
                track = "+".join(track)
                track = track.replace('%25', '%')

                artist = []
                for art in scus[4].split("+"):
                    artist.append(urlquote(art))
                artist = "+".join(artist)
                artist = artist.replace('%25', '%')

                tr['url'] = f"https://www.last.fm/music/{artist}/_/{track}"

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
                nRep += 1
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

    await ctx.edit(sendMessages, embeds=dcEm)


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


@bot.command(
    name="admin_verify",
    description="Verify user for the server, for admin only!",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=[
        int(VERIFICATION_SERVER)
    ],
    options=[
        interactions.Option(
            name="username",
            description="User to verify",
            type=interactions.OptionType.USER,
            required=True
        )
    ]
)
async def admin_verify(ctx: interactions.CommandContext, username: int):
    await ctx.defer()
    discordId = username.id
    # get user joined date
    discordJoined = snowflake_to_datetime(discordId)
    discordJoined = int(discordJoined)
    getMemberDetail = await ctx.guild.get_member(discordId)
    memberRoles = getMemberDetail.roles
    verifiedRole = VERIFIED_ROLE

    try:
        if discordId == ctx.author.id:
            raise Exception(
                f"{EMOJI_USER_ERROR} Sorry, but you can't verify yourself!")
        elif int(verifiedRole) in memberRoles:
            raise Exception(f"{EMOJI_USER_ERROR} User have already verified.")

        with open(database, "r") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if row[0] == discordId:
                    username = row[3]
                    break
            else:
                raise Exception(
                    f"{EMOJI_UNEXPECTED_ERROR} It seems user has been not registered to the bot, or there's unknown error")

        clubs = await checkClubMembership(username)
        verified = False
        for club in clubs:
            if int(club['mal_id']) == int(CLUB_ID):
                botHttp = interactions.HTTPClient(token=BOT_TOKEN)
                await botHttp.add_member_role(guild_id=ctx.guild_id, user_id=discordId, role_id=verifiedRole, reason=f"Verified by {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")
                sendMessages = f"{EMOJI_SUCCESS} User <@!{discordId}> has been verified"
                verified = True
                break

        if verified is False:
            raise Exception(
                f"{EMOJI_DOUBTING} User may have not joined the club yet, or the bot currently only check a page. Please raise an issue to this bot maintainer")
    except Exception as e:
        sendMessages = returnException(e)

    await ctx.send(sendMessages)


print("Starting bot...")

bot.start()
