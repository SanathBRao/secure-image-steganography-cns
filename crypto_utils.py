"""
CNS Mini Project: Secure Image Steganography
Module: crypto_utils.py
Description: Implements cryptographic primitives including:
  1. PBKDF2 (Password-Based Key Derivation Function 2) using HMAC-SHA256
  2. AES-256-GCM (Galois/Counter Mode) Authenticated Encryption
  3. SHA-256 Message Integrity Verification
  4. Structured binary payload packaging and unpacking

Security Guarantees:
  - Confidentiality: AES-256 prevents unauthorized readout even if LSB hiding is detected.
  - Authenticity & Integrity: AES-GCM 128-bit authentication tag detects any tampering,
    bit-flipping, or incorrect password attempts immediately.
  - Hash Verification: SHA-256 hash of original plaintext provides dual-layer verification.
  - Nonce & Salt Freshness: A cryptographically secure random 16-byte salt and 12-byte
    nonce are generated per encryption, preventing replay and rainbow-table attacks.
"""

import hashlib
import os
import struct
from typing import Dict, Any, Tuple
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

# Magic bytes identifying a valid steganographic payload created by this system
MAGIC_HEADER = b"STEG"  # 4 bytes

# Cryptographic parameters
PBKDF2_ITERATIONS = 100_000  # High iteration count resists brute-force / GPU cracking
KEY_SIZE_BYTES = 32          # 256 bits for AES-256
SALT_SIZE_BYTES = 16         # 128-bit random salt
NONCE_SIZE_BYTES = 12        # 96-bit standard nonce for GCM mode
TAG_SIZE_BYTES = 16          # 128-bit authentication tag
HASH_SIZE_BYTES = 32         # 256 bits for SHA-256 digest

# Payload Header structure:
# Magic (4B) + Salt (16B) + Nonce (12B) + Tag (16B) + SHA256 (32B) + Ciphertext_Len (4B)
HEADER_FORMAT = f"!4s{SALT_SIZE_BYTES}s{NONCE_SIZE_BYTES}s{TAG_SIZE_BYTES}s{HASH_SIZE_BYTES}sI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 84 bytes


def derive_key(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """
    Derives a 256-bit (32 bytes) AES encryption key from a user password using PBKDF2.

    Args:
        password (str): User-provided secret passphrase.
        salt (bytes): 16-byte cryptographically secure random salt.
        iterations (int): Iteration count (default: 100,000).

    Returns:
        bytes: 32-byte derived symmetric key.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    if len(salt) != SALT_SIZE_BYTES:
        raise ValueError(f"Salt must be exactly {SALT_SIZE_BYTES} bytes.")

    return PBKDF2(
        password=password.encode("utf-8"),
        salt=salt,
        dkLen=KEY_SIZE_BYTES,
        count=iterations,
        hmac_hash_module=SHA256
    )


def compute_sha256(data: bytes) -> bytes:
    """
    Computes standard SHA-256 digest (32 bytes) for integrity auditing.

    Args:
        data (bytes): Input raw byte sequence.

    Returns:
        bytes: 32-byte raw binary hash digest.
    """
    return hashlib.sha256(data).digest()


def encrypt_message(plaintext: str, password: str) -> Tuple[bytes, Dict[str, Any]]:
    """
    Encrypts a secret plaintext message using AES-256-GCM and packages it into
    a structured binary payload ready for LSB steganography embedding.

    Workflow:
      1. Encode plaintext to UTF-8 bytes and compute SHA-256 digest.
      2. Generate 16-byte random salt and 12-byte random nonce.
      3. Derive 256-bit key via PBKDF2 (HMAC-SHA256, 100k iterations).
      4. Initialize AES-256-GCM cipher and encrypt plaintext.
      5. Obtain ciphertext and 16-byte authentication tag.
      6. Pack header metadata and append ciphertext.

    Args:
        plaintext (str): Secret message to conceal.
        password (str): Passphrase for encryption.

    Returns:
        Tuple[bytes, Dict[str, Any]]:
          - Serialized binary payload
          - Metadata dictionary for inspection/display in UI
    """
    if not plaintext:
        raise ValueError("Secret message cannot be empty.")
    if not password:
        raise ValueError("Password cannot be empty.")

    plaintext_bytes = plaintext.encode("utf-8")
    message_hash = compute_sha256(plaintext_bytes)

    # Cryptographically secure random salt and nonce
    salt = get_random_bytes(SALT_SIZE_BYTES)
    nonce = get_random_bytes(NONCE_SIZE_BYTES)

    # Derive key
    aes_key = derive_key(password, salt)

    # AES-256-GCM Encryption
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext_bytes)

    # Pack into binary payload
    header = struct.pack(
        HEADER_FORMAT,
        MAGIC_HEADER,
        salt,
        nonce,
        auth_tag,
        message_hash,
        len(ciphertext)
    )

    payload = header + ciphertext

    metadata = {
        "plaintext_len": len(plaintext_bytes),
        "ciphertext_len": len(ciphertext),
        "payload_total_bytes": len(payload),
        "salt_hex": salt.hex(),
        "nonce_hex": nonce.hex(),
        "tag_hex": auth_tag.hex(),
        "sha256_hex": message_hash.hex(),
        "iterations": PBKDF2_ITERATIONS,
        "mode": "AES-256-GCM"
    }

    return payload, metadata


def decrypt_message(payload: bytes, password: str) -> Dict[str, Any]:
    """
    Extracts, authenticates, and decrypts a structured payload using AES-256-GCM.

    Verification layers:
      1. Magic Header check (ensures data belongs to this steganography scheme).
      2. AES-GCM Tag verification (validates key + authenticates ciphertext).
      3. SHA-256 hash comparison (double confirms original plaintext integrity).

    Args:
        payload (bytes): Serialized binary payload extracted from image.
        password (str): Passphrase entered by user for extraction.

    Returns:
        Dict[str, Any]:
          - "success": bool
          - "message": str (decrypted plaintext if successful)
          - "error": str (descriptive failure message if unsuccessful)
          - "auth_tag_valid": bool
          - "sha256_match": bool
          - "metadata": dict (extracted crypto parameters)
    """
    result = {
        "success": False,
        "message": "",
        "error": "",
        "auth_tag_valid": False,
        "sha256_match": False,
        "metadata": {}
    }

    if not password:
        result["error"] = "Password cannot be empty."
        return result

    if len(payload) < HEADER_SIZE:
        result["error"] = f"Payload too small ({len(payload)} bytes). Minimum header size is {HEADER_SIZE} bytes."
        return result

    try:
        # Unpack header
        header_bytes = payload[:HEADER_SIZE]
        magic, salt, nonce, auth_tag, expected_hash, ct_len = struct.unpack(HEADER_FORMAT, header_bytes)

        if magic != MAGIC_HEADER:
            result["error"] = "Invalid header: No valid steganographic signature detected. Image may not contain data."
            return result

        ciphertext = payload[HEADER_SIZE:HEADER_SIZE + ct_len]
        if len(ciphertext) != ct_len:
            result["error"] = f"Corrupted payload: expected {ct_len} ciphertext bytes, but got {len(ciphertext)}."
            return result

        result["metadata"] = {
            "salt_hex": salt.hex(),
            "nonce_hex": nonce.hex(),
            "tag_hex": auth_tag.hex(),
            "expected_sha256": expected_hash.hex(),
            "ciphertext_len": ct_len
        }

        # Derive key using provided password and extracted salt
        aes_key = derive_key(password, salt)

        # Attempt AES-GCM Decryption and Tag Verification
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        try:
            decrypted_bytes = cipher.decrypt_and_verify(ciphertext, auth_tag)
            result["auth_tag_valid"] = True
        except (ValueError, KeyError):
            result["auth_tag_valid"] = False
            result["error"] = "Authentication failed! Incorrect password or modified/corrupted image data."
            return result

        # SHA-256 Plaintext Hash Verification
        actual_hash = compute_sha256(decrypted_bytes)
        if actual_hash == expected_hash:
            result["sha256_match"] = True
            result["metadata"]["actual_sha256"] = actual_hash.hex()
        else:
            result["sha256_match"] = False
            result["error"] = "Cryptographic integrity warning: SHA-256 checksum mismatch."
            return result

        # Decode message
        try:
            result["message"] = decrypted_bytes.decode("utf-8")
            result["success"] = True
        except UnicodeDecodeError:
            result["error"] = "Decryption succeeded but data is not valid UTF-8 text."
            return result

        return result

    except Exception as e:
        result["error"] = f"Unexpected decryption error: {str(e)}"
        return result
