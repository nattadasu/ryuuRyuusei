#!/usr/bin/env python3
r"""
# AniList Auth

Terminal helper for authenticating the bot host with AniList (PIN flow).

This is an alternative to `/hostsettings anilist login` on Discord. The
obtained tokens are stored in `database/anilist_token.json`, not `.env`.

Requirements:
* Internet connection
* AniList account
* AniList client ID
* AniList client secret
* Enabled NSFW content on AniList account

Usage:
    python -m modules.oobe.anilistAuth
"""

import asyncio

from classes.excepts import ProviderHttpError
from modules.anilist_token import TOKEN_PATH, exchange_pin, get_authorize_url
from modules.anilist_token import save_token as store_token
from modules.prints import print  # pylint: disable=redefined-builtin


async def main():
    """Main function."""
    print("Hello there! 👋\n")
    print(
        "To authenticate with AniList, we need to open your browser to the AniList website."
    )
    print(f"Authentication URL:\n{get_authorize_url()}\n")
    print("We'll wait for your response 😉")
    auth_code = input("Please input the PIN from the AniList website: ").strip()
    try:
        token = await exchange_pin(auth_code)
    except ProviderHttpError as err:
        print(f"AniList rejected the PIN: {err.message}")
        return
    store_token(token)
    print(f"\nReceived Access Token!\nStored securely in {TOKEN_PATH}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except EOFError:
        print("\n\nExiting...")
