"""
CNS Mini Project: Secure Image Steganography Using AES Encryption and LSB Data Hiding
Module: app.py (Flask Web Application)
Description: Production-ready web server and REST API for embedding and extracting
  AES-256-GCM encrypted payloads inside images via LSB data hiding.
"""

import base64
import io
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image

from crypto_utils import (
    encrypt_message,
    decrypt_message,
    PBKDF2_ITERATIONS,
    HEADER_SIZE
)
from steganography import (
    calculate_capacity,
    embed_data,
    extract_data,
    compute_image_metrics
)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max upload

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_images")


@app.route("/")
def index():
    """Renders the main web application UI."""
    return render_template("index.html")


@app.route("/api/samples", methods=["GET"])
def list_samples():
    """Lists available pre-generated sample cover images."""
    if not os.path.exists(SAMPLE_DIR):
        return jsonify({"samples": []})
    samples = [f for f in os.listdir(SAMPLE_DIR) if f.endswith(".png")]
    return jsonify({"samples": samples})


@app.route("/sample_images/<filename>")
def get_sample_image(filename):
    """Serves sample image files."""
    return send_from_directory(SAMPLE_DIR, filename)


@app.route("/api/capacity", methods=["POST"])
def check_capacity():
    """Calculates image carrier capacity for an uploaded cover image."""
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    file = request.files["image"]
    try:
        img = Image.open(file.stream)
        capacity = calculate_capacity(img)
        return jsonify({"success": True, "capacity": capacity})
    except Exception as e:
        return jsonify({"error": f"Failed to analyze image: {str(e)}"}), 400


@app.route("/api/embed", methods=["POST"])
def api_embed():
    """
    Encrypts secret message via AES-256-GCM and embeds payload into cover image LSBs.
    Returns JSON containing base64 stego PNG data URL and cryptographic telemetry.
    """
    if "image" not in request.files:
        return jsonify({"error": "Cover image is required."}), 400

    file = request.files["image"]
    message = request.form.get("message", "").strip()
    password = request.form.get("password", "")

    if not message:
        return jsonify({"error": "Secret message cannot be empty."}), 400
    if not password:
        return jsonify({"error": "Password cannot be empty."}), 400

    try:
        cover_img = Image.open(file.stream)

        # 1. Encrypt and construct payload
        payload, meta = encrypt_message(message, password)

        # 2. Embed into image LSBs
        stego_img = embed_data(cover_img, payload)

        # 3. Compute quality metrics
        metrics = compute_image_metrics(cover_img, stego_img)

        # 4. Export as PNG to bytes
        buf = io.BytesIO()
        stego_img.save(buf, format="PNG")
        buf.seek(0)
        stego_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        carrier_cap = calculate_capacity(cover_img)["carrier_bytes"]
        cap_used_pct = round(((len(payload) + 4) / carrier_cap) * 100, 4)

        return jsonify({
            "success": True,
            "stego_image_data": f"data:image/png;base64,{stego_b64}",
            "metadata": meta,
            "metrics": {
                "mse": metrics["mse"],
                "psnr_db": metrics["psnr_db"],
                "capacity_used_pct": cap_used_pct
            }
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal embedding failure: {str(e)}"}), 500


@app.route("/api/extract", methods=["POST"])
def api_extract():
    """
    Extracts LSB payload from stego image and performs AES-256-GCM authenticated decryption.
    Returns verification badges, decrypted message, and telemetry.
    """
    if "image" not in request.files:
        return jsonify({"error": "Stego image is required."}), 400

    file = request.files["image"]
    password = request.form.get("password", "")

    if not password:
        return jsonify({"error": "Password cannot be empty."}), 400

    try:
        stego_img = Image.open(file.stream)

        # 1. Extract LSB payload
        payload = extract_data(stego_img)

        # 2. Authenticate and decrypt
        result = decrypt_message(payload, password)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": f"Steganography extraction error: {str(ve)}",
            "auth_tag_valid": False,
            "sha256_match": False
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error during extraction: {str(e)}",
            "auth_tag_valid": False,
            "sha256_match": False
        }), 500


if __name__ == "__main__":
    print("Starting Flask Web Application for Secure Image Steganography...")
    print("Access locally at: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
