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
import asyncio

from modules.commons import *

async def getKitsuMetadata(id, media: str = "anime") -> dict:
    """Get anime metadata from Kitsu"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://kitsu.io/api/edge/{media}/{id}') as resp:
            jsonText = await resp.text()
            jsonFinal = jload(jsonText)
        await session.close()
        return jsonFinal
