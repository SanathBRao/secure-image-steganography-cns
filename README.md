# Secure Image Steganography Using AES-256 Encryption & LSB Data Hiding

A complete, beginner-friendly **Computer Network Security (CNS) Mini Project** developed for a **2-member college team**.

---

## 🌐 Live Public Web App (No Installation Needed!)
The application is deployed publicly on GitHub Pages and runs entirely in your browser using the native Web Crypto API and HTML5 Canvas:  
👉 **[https://sanathbrao.github.io/secure-image-steganography-cns/](https://sanathbrao.github.io/secure-image-steganography-cns/)**

---

## 📌 Project Overview

This project unites **authenticated modern cryptography** and **spatial-domain image steganography** into a single cohesive pipeline:

- **Confidentiality & Authenticity**: The message is encrypted using **AES-256-GCM** (Galois/Counter Mode) with keys derived via **PBKDF2-HMAC-SHA256** (100,000 iterations and a 16-byte random salt). A 128-bit authentication tag and a 256-bit SHA-256 digest guarantee tamper resistance.
- **Concealment**: The resulting binary payload (header + ciphertext) is injected into the Least Significant Bits (LSB) of the 24-bit RGB pixel channels of a cover image.
- **Defense-in-Depth**:
  - Steganography hides the *existence* of the secret communication.
  - Cryptography protects the *contents* if steganographic presence is suspected.

---

## 🚀 Key Features

- **Standard Modern Web App (No Streamlit)**: Built using standard HTML5, CSS3, JavaScript, and a Flask REST API backend (`app.py`).
- **Zero-Installation Live Demo**: Runs client-side on GitHub Pages via browser Web Crypto API, or locally via Python Flask.
- **Zero-Storage Security**: Passwords are never saved in memory or on disk.
- **Authenticated Decryption**: Incorrect passwords and tampered images trigger immediate AES-GCM tag verification failure.
- **Lossless Export**: Generates pure PNG images to preserve bit-level integrity against lossy compression.
- **Telemetry & Quality Metrics**: Live computation of **Mean Squared Error (MSE)** and **Peak Signal-to-Noise Ratio (PSNR > 50 dB)** to demonstrate mathematical invisibility.
- **Comprehensive Test Suite**: Automated verification of 8 core test cases including edge cases, bit-flipping attacks, and capacity constraints.

---

## 📁 Project Structure

```
cns_image_steganography/
├── index.html              # Public entrypoint for GitHub Pages
├── templates/
│   └── index.html          # Flask Web Application template
├── static/
│   ├── style.css           # Modern responsive design & UI cards
│   └── app.js              # Dual-Engine: Flask API client + Web Crypto engine
├── app.py                  # Python Flask web server & REST API
├── crypto_utils.py         # AES-256-GCM, PBKDF2, SHA-256, & payload packaging
├── steganography.py        # 24-bit RGB LSB embedding, extraction, & PSNR/MSE metrics
├── test_stego.py           # Automated test suite (8 unit tests)
├── generate_samples.py     # Script to generate sample cover images
├── sample_images/          # Sample images for testing (landscape, geometric, avatar)
│   ├── sample_landscape.png
│   ├── sample_geometric.png
│   └── sample_avatar.png
├── requirements.txt        # Project dependencies (Flask, Pillow, PyCryptodome, NumPy)
├── CNS_PROJECT_REPORT.md   # Complete academic project report & Viva Q&A
└── README.md               # Quickstart and overview
```

---

## 🛠️ Local Installation & Setup

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.11 or 3.12)
- pip or uv package manager

### 2. Clone Repository
```bash
git clone https://github.com/SanathBRao/secure-image-steganography-cns.git
cd secure-image-steganography-cns
```

### 3. Create a Virtual Environment & Install Dependencies
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Running the Web Application (Flask)

Launch the Flask web server:
```bash
python app.py
```
Open your browser at **`http://localhost:5000`**.

---

## 🧪 Running the Automated Test Suite

To verify all 8 test cases:
```bash
python test_stego.py
```

### Test Case Coverage:
1. `test_01_correct_password_roundtrip`: Verifies encryption, embedding, extraction, and decryption.
2. `test_02_incorrect_password`: Verifies AES-GCM authentication tag rejection upon bad passphrase.
3. `test_03_empty_message`: Verifies input validation on empty messages and empty passwords.
4. `test_04_rgba_format_handling`: Validates transparent RGBA image conversion to RGB.
5. `test_05_insufficient_capacity`: Verifies capacity check when message exceeds carrier pixels.
6. `test_06_tampered_corrupted_stego_image`: Injects bit flips into carrier pixels and confirms detection.
7. `test_07_unicode_and_multiline_message`: Verifies Unicode, symbols, emojis, and multiline text.
8. `test_08_sha256_verification_and_psnr_metrics`: Confirms SHA-256 hash matching and PSNR > 50 dB.

---

## 👥 Suggested 2-Member Team Work Division

| Member | Primary Focus | Key Responsibilities |
|---|---|---|
| **Member 1** | **Cryptography & Key Management** | Implementation of `crypto_utils.py` (AES-256-GCM, PBKDF2 key stretching, random salt & nonce generation, SHA-256 digest, binary header serialization). |
| **Member 2** | **Steganography & Web UI** | Implementation of `steganography.py` & `app.py` / frontend (LSB bitwise embedding/extraction, capacity checks, MSE/PSNR calculation, Flask & Web UI controls, lossless PNG handling). |

---

## 📜 Full Academic Report & Viva Cheat Sheet
See [CNS_PROJECT_REPORT.md](CNS_PROJECT_REPORT.md) for the complete academic write-up, theoretical derivations, algorithms, block diagrams, and 20+ viva questions with model answers.
