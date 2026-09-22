"""
CNS Mini Project: Secure Image Steganography
Module: steganography.py
Description: Implements 24-bit RGB LSB (Least Significant Bit) data hiding,
  extraction, capacity verification, and image quality evaluation (MSE & PSNR).

Key Concepts for Viva:
  - Spatial Domain Technique: Data is hidden directly in the pixel intensities.
  - Invisibility / Imperceptibility: Altering bit 0 changes color value by at most 1 unit
    (e.g., RGB (150, 80, 220) -> (151, 80, 221)), undetectable to the human eye.
  - Lossless Preservation: Must use lossless formats (e.g. PNG). Lossy compression
    (like JPEG) discards high-frequency details and corrupts LSB data.
"""

import math
import struct
from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image

# 4 bytes (32 bits) reserved for storing the length of the embedded payload
LENGTH_HEADER_BYTES = 4


def calculate_capacity(image: Image.Image) -> Dict[str, Any]:
    """
    Calculates the maximum embedding capacity of an image in bits and bytes.

    Args:
        image (Image.Image): PIL Image object.

    Returns:
        Dict[str, Any]: Detailed metrics on width, height, pixels, channels, and capacity.
    """
    width, height = image.size
    total_pixels = width * height
    # Using 3 channels (RGB): 1 bit per channel per pixel = 3 bits per pixel
    total_carrier_bits = total_pixels * 3
    total_carrier_bytes = total_carrier_bits // 8

    # Subtract the 4 bytes used for payload length prefix
    max_payload_bytes = max(0, total_carrier_bytes - LENGTH_HEADER_BYTES)

    return {
        "width": width,
        "height": height,
        "total_pixels": total_pixels,
        "carrier_bits": total_carrier_bits,
        "carrier_bytes": total_carrier_bytes,
        "max_payload_bytes": max_payload_bytes,
        "max_payload_kb": round(max_payload_bytes / 1024, 2)
    }


def embed_data(cover_image: Image.Image, payload: bytes) -> Image.Image:
    """
    Hides a binary payload inside the RGB channels of a cover image using LSB substitution.

    Workflow:
      1. Verify capacity: payload_len + 4 <= total_carrier_bytes.
      2. Convert image to RGB format.
      3. Prepend 4-byte big-endian payload length integer.
      4. Convert complete byte sequence into an array of bits (0s and 1s).
      5. Substitute the LSB of each pixel channel (R, G, B) with payload bits.
      6. Return new stego PIL Image.

    Args:
        cover_image (Image.Image): Input cover image.
        payload (bytes): Encrypted binary payload to embed.

    Returns:
        Image.Image: New stego image containing hidden data.
    """
    # Ensure RGB mode (24-bit color)
    if cover_image.mode != "RGB":
        image_rgb = cover_image.convert("RGB")
    else:
        image_rgb = cover_image.copy()

    capacity_info = calculate_capacity(image_rgb)
    required_bytes = LENGTH_HEADER_BYTES + len(payload)

    if required_bytes > capacity_info["carrier_bytes"]:
        raise ValueError(
            f"Image capacity exceeded! Image can hold {capacity_info['max_payload_bytes']} bytes, "
            f"but payload requires {len(payload)} bytes."
        )

    # Prepend 4-byte length prefix (big-endian unsigned integer)
    length_prefix = struct.pack("!I", len(payload))
    data_to_embed = length_prefix + payload

    # Convert bytes into a flat list of bits (MSB first)
    bits = []
    for byte in data_to_embed:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    total_bits_to_embed = len(bits)

    # Convert image pixels to a 1D NumPy array for high-performance bitwise ops
    pixels = np.array(image_rgb, dtype=np.uint8)
    flat_pixels = pixels.reshape(-1)

    # Substitute LSB: (pixel & 0xFE) | bit
    # 0xFE in binary is 11111110, clearing the least significant bit
    bit_array = np.array(bits, dtype=np.uint8)
    flat_pixels[:total_bits_to_embed] = (flat_pixels[:total_bits_to_embed] & 0xFE) | bit_array

    # Reshape back to image dimensions and create new PIL Image
    stego_pixels = flat_pixels.reshape(pixels.shape)
    stego_image = Image.fromarray(stego_pixels, mode="RGB")

    return stego_image


def extract_data(stego_image: Image.Image) -> bytes:
    """
    Extracts embedded binary payload from the LSBs of an RGB stego image.

    Workflow:
      1. Read the first 32 bits (4 bytes) from pixel channels to determine payload length N.
      2. Validate that N is within physical carrier capacity limits.
      3. Read the subsequent N * 8 bits.
      4. Reconstruct and return the N payload bytes.

    Args:
        stego_image (Image.Image): Image suspected of containing hidden data.

    Returns:
        bytes: Extracted binary payload.
    """
    if stego_image.mode != "RGB":
        image_rgb = stego_image.convert("RGB")
    else:
        image_rgb = stego_image

    capacity_info = calculate_capacity(image_rgb)
    total_carrier_bits = capacity_info["carrier_bits"]

    # Minimum bits required is 32 bits for the length header
    if total_carrier_bits < LENGTH_HEADER_BYTES * 8:
        raise ValueError("Image is too small to contain a steganographic header.")

    pixels = np.array(image_rgb, dtype=np.uint8)
    flat_pixels = pixels.reshape(-1)

    # Extract LSB of each pixel channel: pixel & 1
    # Step 1: Read the 32 bits of the length header
    header_bits = flat_pixels[:LENGTH_HEADER_BYTES * 8] & 1
    
    # Pack bits into 4 bytes
    length_bytes = bytearray()
    for byte_idx in range(LENGTH_HEADER_BYTES):
        byte_val = 0
        for bit_idx in range(8):
            bit = header_bits[byte_idx * 8 + bit_idx]
            byte_val = (byte_val << 1) | int(bit)
        length_bytes.append(byte_val)

    payload_length = struct.unpack("!I", bytes(length_bytes))[0]

    # Sanity checks on payload length
    if payload_length == 0:
        raise ValueError("No hidden data found: embedded length prefix is 0.")

    if payload_length > capacity_info["max_payload_bytes"]:
        raise ValueError(
            f"Extracted payload length ({payload_length} bytes) exceeds maximum "
            f"carrier capacity ({capacity_info['max_payload_bytes']} bytes). "
            "The image may not contain valid steganographic data or was modified."
        )

    # Step 2: Read payload bits
    start_bit = LENGTH_HEADER_BYTES * 8
    end_bit = start_bit + (payload_length * 8)
    payload_bits = flat_pixels[start_bit:end_bit] & 1

    # Reassemble bytes
    payload = bytearray(payload_length)
    for byte_idx in range(payload_length):
        byte_val = 0
        for bit_idx in range(8):
            bit = payload_bits[byte_idx * 8 + bit_idx]
            byte_val = (byte_val << 1) | int(bit)
        payload[byte_idx] = byte_val

    return bytes(payload)


def compute_image_metrics(original_image: Image.Image, stego_image: Image.Image) -> Dict[str, float]:
    """
    Computes objective image quality metrics between cover and stego images:
      - MSE (Mean Squared Error): Measures average squared pixel difference.
      - PSNR (Peak Signal-to-Noise Ratio): Logarithmic measure of imperceptibility in decibels (dB).

    Typical values for 1-bit LSB steganography:
      - MSE: < 0.5 (virtually indistinguishable)
      - PSNR: > 50 dB (values > 30 dB are considered visually invisible)

    Args:
        original_image (Image.Image): Original cover image.
        stego_image (Image.Image): Stego image after embedding.

    Returns:
        Dict[str, float]: Calculated MSE and PSNR (dB).
    """
    orig_rgb = original_image.convert("RGB") if original_image.mode != "RGB" else original_image
    stego_rgb = stego_image.convert("RGB") if stego_image.mode != "RGB" else stego_image

    if orig_rgb.size != stego_rgb.size:
        raise ValueError("Images must have identical dimensions to compute metrics.")

    arr1 = np.array(orig_rgb, dtype=np.float64)
    arr2 = np.array(stego_rgb, dtype=np.float64)

    mse = float(np.mean((arr1 - arr2) ** 2))

    if mse == 0:
        psnr = float("inf")  # Perfect identical images
    else:
        max_pixel = 255.0
        psnr = float(20 * math.log10(max_pixel / math.sqrt(mse)))

    return {
        "mse": round(mse, 6),
        "psnr_db": round(psnr, 2) if psnr != float("inf") else 999.0
    }
