# from modules.classes.simkl import Simkl
import asyncio
import json
import time
from os import getenv as ge

from dotenv import load_dotenv as ld
from interactions import Member

from classes.animeapi import AnimeApi
from classes.database import UserDatabase
from classes.simkl import Simkl, SimklMediaTypes
from classes.spotify import SpotifyApi
from main import bot

ld()

simkl_client_id = ge('SIMKL_CLIENT_ID')


async def simklfunc():
    start = time.time()
    async with Simkl(simkl_client_id) as simkl:
        data = await simkl.get_title_ids(37089, SimklMediaTypes.ANIME)
        print(data)
    end = time.time()
    total = end - start
    print(f"Total time: {total} seconds")


async def aniapi():
    start = time.time()
    async with AnimeApi() as api:
        data = await api.get_relation(1, api.AnimeApiPlatforms.MAL)
        print(data)
    end = time.time()
    total = end - start
    print(f"Total time: {total} seconds")


async def db():
    start = time.time()
    async with UserDatabase() as db:
        isExist = await db.check_if_registered(384089845527478272)
        print(isExist)
        data = await db.export_user_data(384089845527478272)
        print(data)
    end = time.time()
    total = end - start
    print(f"Total time: {total} seconds")


async def test_member():
    start = time.time()
    member = await bot.http.get_member(guild_id=589128995501637655, user_id=384089845527478272)
    member = Member.from_dict(member)
    print(member)
    end = time.time()
    total = end - start
    print(f"Total time: {total} seconds")


async def spotify():
    async with SpotifyApi() as spot:
        # search = await spot.search("Lathi", spot.MediaType.TRACK)
        # print(search["tracks"]["items"][0])
        track = await spot.get_track("06pezDUwqVsUfpBNw6uJir")
        print(json.dumps(track, indent=4))

asyncio.run(simklfunc())
