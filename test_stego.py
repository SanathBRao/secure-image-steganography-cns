"""
CNS Mini Project: Secure Image Steganography
Module: test_stego.py
Description: Automated test suite validating all 8 core security and steganographic
  requirements for academic assessment and project demonstration.

Test Cases:
  1. Correct password roundtrip test
  2. Incorrect password rejection & graceful failure
  3. Empty message input validation
  4. Non-RGB image format normalization (RGBA to RGB conversion)
  5. Insufficient image capacity detection
  6. Tampered / corrupted stego image detection (bit-flipping attacks)
  7. Large multiline & Unicode (emojis / special symbols) secret message
  8. SHA-256 plaintext integrity validation
"""

import os
import unittest
import numpy as np
from PIL import Image

from crypto_utils import (
    encrypt_message,
    decrypt_message,
    compute_sha256,
    MAGIC_HEADER,
    HEADER_SIZE
)
from steganography import (
    calculate_capacity,
    embed_data,
    extract_data,
    compute_image_metrics
)


class TestSecureSteganography(unittest.TestCase):

    def setUp(self):
        # Create standard 200x200 test RGB image
        self.cover_image = Image.new("RGB", (200, 200), color=(100, 150, 200))
        self.password = "TopSecret@CNS2026"
        self.message = "Confidential CNS Mini Project Message: Meet at Server Room 4 at 14:00."

    def test_01_correct_password_roundtrip(self):
        """Test Case 1: Standard roundtrip with correct password must decrypt perfectly."""
        # 1. Encrypt
        payload, meta = encrypt_message(self.message, self.password)
        self.assertEqual(payload[:4], MAGIC_HEADER)
        
        # 2. Embed into image
        stego_img = embed_data(self.cover_image, payload)
        
        # 3. Extract from image
        extracted_payload = extract_data(stego_img)
        self.assertEqual(payload, extracted_payload)
        
        # 4. Decrypt
        res = decrypt_message(extracted_payload, self.password)
        self.assertTrue(res["success"])
        self.assertTrue(res["auth_tag_valid"])
        self.assertTrue(res["sha256_match"])
        self.assertEqual(res["message"], self.message)

    def test_02_incorrect_password(self):
        """Test Case 2: Incorrect password must fail GCM tag verification gracefully."""
        payload, _ = encrypt_message(self.message, self.password)
        stego_img = embed_data(self.cover_image, payload)
        extracted_payload = extract_data(stego_img)

        wrong_password = "WrongPassword999!"
        res = decrypt_message(extracted_payload, wrong_password)

        self.assertFalse(res["success"])
        self.assertFalse(res["auth_tag_valid"])
        self.assertIn("Authentication failed", res["error"])
        self.assertEqual(res["message"], "")

    def test_03_empty_message(self):
        """Test Case 3: Empty secret message or empty password must be rejected."""
        with self.assertRaises(ValueError):
            encrypt_message("", self.password)

        with self.assertRaises(ValueError):
            encrypt_message(self.message, "")

    def test_04_rgba_format_handling(self):
        """Test Case 4: Images with Alpha channel (RGBA) must be converted and work seamlessly."""
        rgba_img = Image.new("RGBA", (200, 200), color=(80, 120, 160, 200))
        payload, _ = encrypt_message(self.message, self.password)

        stego_img = embed_data(rgba_img, payload)
        self.assertEqual(stego_img.mode, "RGB")

        extracted_payload = extract_data(stego_img)
        res = decrypt_message(extracted_payload, self.password)
        self.assertTrue(res["success"])
        self.assertEqual(res["message"], self.message)

    def test_05_insufficient_capacity(self):
        """Test Case 5: An image too small for the payload must raise a capacity ValueError."""
        # 5x5 image has 25 pixels * 3 channels = 75 bits = 9 bytes capacity.
        # Header alone requires 84 bytes.
        tiny_img = Image.new("RGB", (5, 5), color=(255, 255, 255))
        payload, _ = encrypt_message(self.message, self.password)

        with self.assertRaises(ValueError) as ctx:
            embed_data(tiny_img, payload)
        self.assertIn("capacity exceeded", str(ctx.exception).lower())

    def test_06_tampered_corrupted_stego_image(self):
        """Test Case 6: Bit flipping in the stego image must trigger AES-GCM or length corruption detection."""
        payload, _ = encrypt_message(self.message, self.password)
        stego_img = embed_data(self.cover_image, payload)

        # Intentionally tamper with the stego image pixels within the embedded payload range
        # Flat channel index 50 is inside the embedded header (salt/nonce/tag)
        pixels = np.array(stego_img)
        flat = pixels.reshape(-1)
        flat[50] = flat[50] ^ 1  # Flip LSB of an embedded carrier channel
        tampered_img = Image.fromarray(flat.reshape(pixels.shape), mode="RGB")

        try:
            extracted_payload = extract_data(tampered_img)
            res = decrypt_message(extracted_payload, self.password)
            # If payload was extracted, AES-GCM tag verification or magic header must fail
            self.assertFalse(res["success"])
            self.assertFalse(res["auth_tag_valid"])
        except ValueError:
            # Or length prefix / capacity check was corrupted, which also cleanly catches the tampering
            pass

    def test_07_unicode_and_multiline_message(self):
        """Test Case 7: Secret message with emojis, UTF-8 symbols, and newlines."""
        special_msg = (
            "🔐 Top Secret Operational Briefing 🚀\n"
            "• Node Coordinates: 37.7749° N, 122.4194° W\n"
            "• Status: 100% Operational! 🛡️\n"
            "• Cipher: AES-256-GCM authenticated."
        )
        payload, _ = encrypt_message(special_msg, self.password)
        stego_img = embed_data(self.cover_image, payload)
        extracted = extract_data(stego_img)
        res = decrypt_message(extracted, self.password)

        self.assertTrue(res["success"])
        self.assertEqual(res["message"], special_msg)

    def test_08_sha256_verification_and_psnr_metrics(self):
        """Test Case 8: Verify SHA-256 integrity digest and high visual quality (PSNR > 50 dB)."""
        payload, meta = encrypt_message(self.message, self.password)
        stego_img = embed_data(self.cover_image, payload)
        extracted = extract_data(stego_img)
        res = decrypt_message(extracted, self.password)

        # Check SHA-256 matches plaintext digest
        expected_sha = compute_sha256(self.message.encode("utf-8")).hex()
        self.assertEqual(res["metadata"]["expected_sha256"], expected_sha)
        self.assertEqual(res["metadata"]["actual_sha256"], expected_sha)
        self.assertTrue(res["sha256_match"])

        # Check image quality metrics
        metrics = compute_image_metrics(self.cover_image, stego_img)
        self.assertLess(metrics["mse"], 0.5)  # MSE is minimal
        self.assertGreater(metrics["psnr_db"], 50.0)  # High PSNR indicates imperceptibility


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSecureSteganography)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
