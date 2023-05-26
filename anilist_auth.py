"""
# AniList Auth

This script contains the functions for authenticating with AniList.

Requirements:
* Internet connection
* AniList account
* AniList client ID
* AniList client secret
* Enabled NSFW content on AniList account
"""

import asyncio
import aiohttp
import urllib.parse
from modules.const import (
    ANILIST_CLIENT_ID,
    ANILIST_CLIENT_SECRET,
    ANILIST_REDIRECT_URI,
    ANILIST_USERNAME,
)
from datetime import datetime, timezone


async def get_auth_code():
    """
    Get the authentication code from AniList.
    """
    auth_endpoint = "https://anilist.co/api/v2/oauth/authorize"
    client_id_param = f"client_id={ANILIST_CLIENT_ID}"
    redirect_uri_param = f'redirect_uri={urllib.parse.quote(ANILIST_REDIRECT_URI, "")}'
    response_param = "response_type=code"
    get_auth_code = (
        f"{auth_endpoint}?{client_id_param}&{redirect_uri_param}&{response_param}"
    )
    print(f"Hello there, {ANILIST_USERNAME}! 👋\n")
    print(
        "To authenticate with AniList, we need to open your browser to the AniList website."
    )
    print(f"Authentication URL:\n{get_auth_code}\n")
    print("We'll wait for your response 😉")


async def fetch_access_token(auth_code: str):
    token_endpoint = "https://anilist.co/api/v2/oauth/token"
    client_id_param = f"client_id={ANILIST_CLIENT_ID}"
    client_secret_param = f"client_secret={ANILIST_CLIENT_SECRET}"
    redirect_uri_param = f"redirect_uri={urllib.parse.quote(ANILIST_REDIRECT_URI)}"
    json_req = {
        "grant_type": "authorization_code",
        "client_id": ANILIST_CLIENT_ID,
        "client_secret": ANILIST_CLIENT_SECRET,
        "redirect_uri": ANILIST_REDIRECT_URI,
        "code": auth_code,
    }
    token_uri = (
        f"{token_endpoint}?{client_id_param}&{client_secret_param}&{redirect_uri_param}"
    )
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(token_uri, json=json_req, headers=headers) as response:
            token = await response.json()
            now = int(datetime.now(tz=timezone.utc).timestamp())
            token["expires_in"] += now
            return token


async def main():
    await get_auth_code()
    auth_code = input("Please input the code from the AniList website: ")
    token = await fetch_access_token(auth_code)
    print("Received Access Token!\n")
    print("Please copy this value to your ENV file:\n")
    print("ANILIST_ACCESS_TOKEN=", end="")
    print(token["access_token"])
    print("ANILIST_OAUTH_REFRESH=", end="")
    print(token["refresh_token"])
    print("ANILIST_OAUTH_EXPIRY=", end="")
    print(token["expires_in"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except EOFError:
        print("\n\nExiting...")
