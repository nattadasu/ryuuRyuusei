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


async def export_backup(output_path: str):
    import tempfile

    try:
        print("Packaging files...")
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir_to_archive = Path(tmpdir) / "backup_content"
            temp_dir_to_archive.mkdir()

            # Add database directory
            if os.path.exists("database"):
                shutil.copytree(
                    "database", temp_dir_to_archive / "database", dirs_exist_ok=True
                )
                print("Added 'database' folder to backup.")

            # Add .env file
            if os.path.exists(".env"):
                shutil.copy2(".env", temp_dir_to_archive / ".env")
                print("Added '.env' file to backup.")

            # Add any private_ files/folders (e.g., extensions/private_seasonal.py)
            private_count = 0
            for path in Path(".").rglob("private_*"):
                if (
                    "__pycache__" in str(path)
                    or ".mypy_cache" in str(path)
                    or ".ruff_cache" in str(path)
                ):
                    continue

                relative_path = path.relative_to(".")
                dest_path = temp_dir_to_archive / relative_path

                if path.is_dir():
                    shutil.copytree(path, dest_path, dirs_exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest_path)
                private_count += 1

            if private_count > 0:
                print(f"Added {private_count} private files/folders to backup.")

            # Create tar archive
            archive_path_base = Path(tmpdir) / "backup"
            archive_path = Path(
                shutil.make_archive(
                    str(archive_path_base), "tar", root_dir=temp_dir_to_archive
                )
            )

            print("Compressing and encrypting backup...")
            enc_path, key = CryptoUtils.encrypt_and_package(archive_path)

            final_path = Path(output_path)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            if final_path.exists():
                final_path.unlink()
            shutil.move(enc_path, final_path)

            print(f"Backup exported successfully to {final_path}")
            print(f"Encryption Key: {key}")
            print("Please save this key in a secure place. It is required to decrypt/import the backup.")

    except Exception as e:
        print(f"An error occurred during export: {e}")


if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(description="Backup utility for import and export.")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Import parser
    import_parser = subparsers.add_parser("import", help="Import an encrypted backup")
    import_parser.add_argument("file", help="The encrypted backup file (.enc)")
    import_parser.add_argument("key", help="The encryption key")

    # Export parser
    export_parser = subparsers.add_parser("export", help="Export an encrypted backup")
    export_parser.add_argument(
        "-o", "--output", default="backup.tar.gz.enc", help="The output encrypted backup file path"
    )

    if len(sys.argv) == 3 and sys.argv[1] not in ("import", "export"):
        asyncio.run(import_backup(sys.argv[1], sys.argv[2]))
    else:
        subparsers.required = True
        args = parser.parse_args()
        if args.action == "import":
            asyncio.run(import_backup(args.file, args.key))
        elif args.action == "export":
            asyncio.run(export_backup(args.output))
