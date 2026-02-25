import argparse
import asyncio
import os
import shutil
import tarfile
from pathlib import Path

import aiohttp

from modules.crypto_utils import CryptoUtils


async def import_backup(file_path: str, key: str):
    temp_enc_path = Path("backup_temp.enc")
    temp_tar_path = Path("backup_temp.tar")
    is_url = file_path.startswith(("http://", "https://"))

    try:
        if is_url:
            print(f"Downloading backup from {file_path}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(file_path) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        temp_enc_path.write_bytes(data)
                    else:
                        raise Exception(
                            f"Failed to download attachment: HTTP {resp.status}"
                        )
            print("Download complete.")
        else:
            temp_enc_path = Path(file_path)
            if not temp_enc_path.exists():
                print(f"Error: File {file_path} not found.")
                return

        print("Decrypting backup...")
        CryptoUtils.decrypt_and_extract(temp_enc_path, key, temp_tar_path)

        # Create backup of current state
        print("Creating backup of current state...")
        if os.path.exists("database"):
            if os.path.exists("database_backup"):
                shutil.rmtree("database_backup")
            shutil.copytree("database", "database_backup")
            print("Current 'database' folder backed up to 'database_backup'.")

        if os.path.exists(".env"):
            shutil.copy2(".env", ".env.bak")
            print("Current '.env' backed up to '.env.bak'.")

        # Extract tar
        print("Extracting files...")
        with tarfile.open(temp_tar_path, "r") as tar:
            tar.extractall(path=".")

        print("Backup imported successfully!")

    except Exception as e:
        print(f"An error occurred during import: {e}")
    finally:
        if temp_tar_path.exists():
            temp_tar_path.unlink()
        if is_url and temp_enc_path.exists():
            temp_enc_path.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import an encrypted backup.")
    parser.add_argument("file", help="The encrypted backup file (.enc)")
    parser.add_argument("key", help="The encryption key")

    args = parser.parse_args()
    asyncio.run(import_backup(args.file, args.key))
