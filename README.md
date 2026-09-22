# Secure Image Steganography Using AES-256 Encryption & LSB Data Hiding

A complete, beginner-friendly **Computer Network Security (CNS) Mini Project** developed for a **2-member college team**.

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

- **Modern Web Dashboard**: Interactive Streamlit interface with dedicated tabs for Embedding, Extraction, System Architecture, and Academic Viva Prep.
- **Zero-Storage Security**: Passwords are never saved in memory or on disk.
- **Authenticated Decryption**: Incorrect passwords and tampered images trigger immediate AES-GCM tag verification failure.
- **Lossless Export**: Generates pure PNG images to preserve bit-level integrity against lossy compression.
- **Telemetry & Quality Metrics**: Live computation of **Mean Squared Error (MSE)** and **Peak Signal-to-Noise Ratio (PSNR > 50 dB)** to demonstrate mathematical invisibility.
- **Comprehensive Test Suite**: Automated verification of 8 core test cases including edge cases, bit-flipping attacks, and capacity constraints.

---

## 📁 Project Structure

```
cns_image_steganography/
├── app.py                  # Streamlit Web Application
├── crypto_utils.py         # AES-256-GCM, PBKDF2, SHA-256, & payload packaging
├── steganography.py        # 24-bit RGB LSB embedding, extraction, & PSNR/MSE metrics
├── test_stego.py           # Automated test suite (8 unit tests)
├── generate_samples.py     # Script to generate sample cover images
├── sample_images/          # Sample images for testing (landscape, geometric, avatar)
│   ├── sample_landscape.png
│   ├── sample_geometric.png
│   └── sample_avatar.png
├── requirements.txt        # Project dependencies
├── CNS_PROJECT_REPORT.md   # Complete academic project report & Viva Q&A
└── README.md               # Quickstart and overview
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.11 or 3.12)
- pip or uv package manager

### 2. Clone or Navigate to Directory
```bash
cd C:\Users\santh\.gemini\antigravity\scratch\cns_image_steganography
```

### 3. Create a Virtual Environment
Using standard Python:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

*Or using `uv` (recommended for ultra-fast setup):*
```bash
uv venv --python 3.12 .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
```

---

## ▶️ Running the Application

Launch the Streamlit web dashboard:
```bash
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running the Automated Test Suite

To verify all 8 test cases:
```bash
.\.venv\Scripts\python.exe test_stego.py
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
| **Member 2** | **Steganography & User Interface** | Implementation of `steganography.py` & `app.py` (LSB bitwise embedding/extraction, capacity checks, MSE/PSNR calculation, Streamlit UI controls, lossless PNG handling). |

---

## 📜 Full Academic Report & Viva Cheat Sheet
See [CNS_PROJECT_REPORT.md](CNS_PROJECT_REPORT.md) for the complete academic write-up, theoretical derivations, algorithms, block diagrams, and 20+ viva questions with model answers.
