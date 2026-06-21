import os
from cryptography.fernet import Fernet

# 1. Fetch the key from the environment variables
_encryption_key_raw = os.getenv("ENCRYPTION_KEY")

if not _encryption_key_raw:
    raise ValueError("Critical Error: 'ENCRYPTION_KEY' environment variable is missing!\n Use Fernet.generate_key() to create one and save in .env")

# 2. Convert the string from the env into bytes and initialize Fernet
try:
    cipher_suite = Fernet(_encryption_key_raw.encode('utf-8'))
except Exception as e:
    raise ValueError(f"Invalid ENCRYPTION_KEY format. Fernet keys must be 32 url-safe base64-encoded bytes. Error: {e}")


def encrypt(data: str) -> str:
    """
    Encrypt data so it can be safely stored and decrypted later.
    """
    # Fernet requires bytes, so we encode the string
    encoded_key = data.encode('utf-8')
    encrypted_bytes = cipher_suite.encrypt(encoded_key)

    # Return as a string for easy database storage
    return encrypted_bytes.decode('utf-8')


def decrypt(encrypted_data: str) -> str:
    """
    Decrypt the stored string back into the original data.
    """
    encrypted_bytes = encrypted_data.encode('utf-8')
    decrypted_bytes = cipher_suite.decrypt(encrypted_bytes)

    # Return as the original string
    return decrypted_bytes.decode('utf-8')