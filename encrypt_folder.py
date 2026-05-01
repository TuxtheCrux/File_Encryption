#!/home/linusr/.venv/bin/python
import os
import pathlib
import argparse
from getpass import getpass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt a file or directory"
    )
    subparsers = parser.add_subparsers()
    encrypt_parser = subparsers.add_parser(
        "encrypt", help="Encrypt a file or directory"
    )
    encrypt_parser.add_argument(
        "path", type=pathlib.Path, help="Path to the file or directory to encrypt"
    )
    encrypt_parser.set_defaults(func=encrypt)
    decrypt_parser = subparsers.add_parser(
        "decrypt", help="Decrypt a file or directory"
    )
    decrypt_parser.add_argument(
        "path", type=pathlib.Path, help="Path to the file or directory to decrypt"
    )
    decrypt_parser.set_defaults(func=decrypt)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    while True:
        if args.path.exists():
            break
        else:
            print(f"Path '{args.path}' does not exist. Please provide a valid path.")
            args.path = pathlib.Path(input("Enter path: "))
    if args.func == encrypt:
        while True:
            password = getpass("Enter password: ")
            validate_password = getpass("Confirm password: ")
            if password == validate_password:
                break
            else:
                print("Passwords do not match. Please try again.")
    elif args.func == decrypt:
        password = getpass("Password: ")
    args.func(args.path, password)


def encrypt(path, password):
    if not path.is_relative_to(pathlib.Path.home()) or any(
        part.startswith(".") for part in path.parts
    ):
        print(
            "Cannot encrypt files in directories starting with a dot or that is not in the home directory."
        )
        return
    if path.is_file():
        encrypt_file(path, password)
    elif path.is_dir():
        encrypt_directory(path, password)


def encrypt_directory(path, password):
    for file in path.rglob("*"):
        if file.is_file() and file.suffix != ".enc":
            encrypt_file(file, password)


def encrypt_file(path, password):
    salt = os.urandom(32)
    nonce = os.urandom(12)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password.encode())
    aesgcm = AESGCM(key=key)
    with open(path, "rb") as file:
        data = file.read()
    encrypted_data = aesgcm.encrypt(nonce, data, None)
    try:
        with open(path.with_suffix(".enc"), "wb") as file:
            file.write(salt)
            file.write(nonce)
            file.write(encrypted_data)
        path.unlink()
    except Exception as e:
        print(f"Error encrypting file: {e}")


def decrypt_file(path, password):
    output_path = path.with_suffix("")
    if output_path.exists():
        print(f"File '{output_path}' already exists. Skipping decryption.")
        return
    with open(path, "rb") as file:
        salt = file.read(32)
        nonce = file.read(12)
        encrypted_data = file.read()
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password.encode())
    aesgcm = AESGCM(key=key)
    try:
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
        with open(path.with_suffix(""), "wb") as file:
            file.write(decrypted_data)
        path.unlink()
    except InvalidTag:
        print("Invalid tag. File may be corrupted.")
    except Exception as e:
        print(f"Error decrypting file: {e}")


def decrypt_directory(path, password):
    for file in path.rglob("*"):
        if file.is_file() and file.suffix == ".enc":
            decrypt_file(file, password)


def decrypt(path, password):
    if path.is_file():
        decrypt_file(path, password)
    elif path.is_dir():
        decrypt_directory(path, password)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
