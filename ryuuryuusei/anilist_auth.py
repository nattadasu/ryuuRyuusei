r"""
# AniList Auth

This script contains the functions for authenticating with AniList.

Requirements:
* Internet connection
* AniList account
* AniList client ID
* AniList client secret
* Enabled NSFW content on AniList account

Attribution Notice:
This script was translated from Modules/Get-AniListAuth.ps1 (yes, PowerShell script)
on nattadasu's/Animanga-Initiative's animeManga-autoBackup repository under MIT License
using OpenAI's ChatGPT-3 engine.

*You might say, why would you attribute a PowerShell script on a Python project?*
Simple, it was me who wrote that PowerShell script. ¯\_(ツ)_/¯

Source:
https://github.com/Animanga-Initiative/animeManga-autoBackup/blob/main/Modules/Get-AniListAuth.ps1
"""

import asyncio
import urllib.parse
from datetime import datetime, timezone

import aiohttp

from modules.const import (ANILIST_CLIENT_ID, ANILIST_CLIENT_SECRET,
                           ANILIST_REDIRECT_URI)


async def get_auth_code():
    """Get the authentication code from AniList."""
    auth_endpoint = "https://anilist.co/api/v2/oauth/authorize"
    client_id_param = f"client_id={ANILIST_CLIENT_ID}"
    redirect_uri_param = f'redirect_uri={urllib.parse.quote(ANILIST_REDIRECT_URI, "")}'
    response_param = "response_type=code"
    url_auth = (
        f"{auth_endpoint}?{client_id_param}&{redirect_uri_param}&{response_param}"
    )
    print("Hello there! 👋\n")
    print(
        "To authenticate with AniList, we need to open your browser to the AniList website."
    )
    print(f"Authentication URL:\n{url_auth}\n")
    print("We'll wait for your response 😉")


async def fetch_access_token(auth_code: str):
    """Fetch the access token from AniList."""
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
    async with aiohttp.ClientSession() as session, session.post(
        token_uri, json=json_req, headers=headers
    ) as response:
        token = await response.json()
        now = int(datetime.now(tz=timezone.utc).timestamp())
        token["expires_in"] += now
        return token


async def main():
    """Main function."""
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
