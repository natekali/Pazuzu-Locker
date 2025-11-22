"""Cryptographic operations for file encryption and decryption."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from cryptography.fernet import Fernet

if TYPE_CHECKING:
    pass


def generate_key() -> bytes:
    """Generate a new Fernet encryption key.
    
    Returns:
        32-byte encryption key.
    """
    return Fernet.generate_key()


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypt data using Fernet symmetric encryption.
    
    Args:
        data: Plaintext data to encrypt.
        key: Fernet encryption key.
    
    Returns:
        Encrypted data.
    """
    cipher = Fernet(key)
    return cipher.encrypt(data)


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypt data using Fernet symmetric encryption.
    
    Args:
        encrypted_data: Encrypted data.
        key: Fernet encryption key.
    
    Returns:
        Decrypted plaintext data.
    """
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data)


def encode_key(key: bytes) -> str:
    """Encode a binary key to base64 string for storage.
    
    Args:
        key: Binary encryption key.
    
    Returns:
        Base64-encoded string.
    """
    return base64.b64encode(key).decode("utf-8")


def decode_key(encoded_key: str) -> bytes:
    """Decode a base64 key string to binary.
    
    Args:
        encoded_key: Base64-encoded key string.
    
    Returns:
        Binary encryption key.
    """
    return base64.b64decode(encoded_key)
