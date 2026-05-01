# File_Encryption
A Python CLI tool for encrypting and decrypting files and directories. Built with cryptography – AES-256-GCM + Scrypt. Includes safeguards against encrypting system paths or hidden directories.

## Features

- Encrypt and decrypt single files or entire directories recursively
- AES-256-GCM for authenticated encryption – detects tampering automatically
- Scrypt for password-based key derivation – resistant to brute-force attacks
- Per-file random salt and nonce – identical files produce different ciphertext
- Path safety checks – prevents accidental encryption of system or hidden directories

## Requirements

- Python 3.8+
- `cryptography` library

```bash
pip install cryptography
```

## Installation

```bash
git clone https://github.com/yourusername/file-encryptor.git
cd file-encryptor
pip install cryptography
```

## Usage

### Encrypt a file

```bash
python encryptor.py encrypt /home/user/documents/file.txt
```

### Encrypt a directory

```bash
python encryptor.py encrypt /home/user/documents/
```

### Decrypt a file

```bash
python encryptor.py decrypt /home/user/documents/file.txt.enc
```

### Decrypt a directory

```bash
python encryptor.py decrypt /home/user/documents/
```

Encrypted files are saved with the `.enc` extension. The original file is deleted after successful encryption.

## Security

- Encryption only works on paths inside the user's home directory
- Paths containing hidden directories (starting with `.`) are rejected
- A wrong password or tampered file will produce an `InvalidTag` error – no data is modified
- **There is no password recovery.** A lost password means permanent data loss.

## How it works

Each file is encrypted independently:

```
[ Salt (32 bytes) ][ Nonce (12 bytes) ][ Ciphertext + GCM Auth-Tag ]
```

The salt and nonce are stored alongside the ciphertext inside the `.enc` file, so no separate metadata file is needed.

## License

This project is licensed under the **GNU General Public License v3.0** – see [LICENSE](LICENSE) for details.
