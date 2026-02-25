import gzip
import shutil
from pathlib import Path

from cryptography.fernet import Fernet


class CryptoUtils:
    @staticmethod
    def encrypt_and_package(file_path: Path) -> tuple[Path, str]:
        """Compresses, encrypts, and packages a file."""
        key = Fernet.generate_key()
        f = Fernet(key)

        # Compress
        gz_path = file_path.with_suffix(file_path.suffix + ".gz")
        with open(file_path, "rb") as f_in:
            with gzip.open(gz_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Encrypt
        with open(gz_path, "rb") as f_in:
            encrypted_data = f.encrypt(f_in.read())

        enc_path = gz_path.with_suffix(gz_path.suffix + ".enc")
        with open(enc_path, "wb") as f_out:
            f_out.write(encrypted_data)

        # Clean up intermediate file
        gz_path.unlink()

        return enc_path, key.decode()

    @staticmethod
    def decrypt_and_extract(encrypted_path: Path, key: str, output_path: Path) -> None:
        """Decrypts and decompresses a file."""
        f = Fernet(key.encode())

        # Decrypt
        with open(encrypted_path, "rb") as f_in:
            decrypted_data = f.decrypt(f_in.read())

        # Save to temporary gz file
        gz_path = encrypted_path.with_suffix("")
        with open(gz_path, "wb") as f_out:
            f_out.write(decrypted_data)

        # Decompress
        with gzip.open(gz_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Clean up intermediate file
        gz_path.unlink()
