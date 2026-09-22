"""
CNS Mini Project: Secure Image Steganography Using AES Encryption and LSB Data Hiding
Application: app.py (Streamlit Web Dashboard)
Designed for: 2-Member College Team Project Presentation and Viva Demonstration
"""

import io
import os
import streamlit as st
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

# Set page configuration
st.set_page_config(
    page_title="Secure Steganography | AES + LSB",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: white;
        font-size: 2.1rem;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        color: #e0e8f9;
        font-size: 1.05rem;
        margin-top: 8px;
        margin-bottom: 0;
    }
    .stCard {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 18px;
        border: 1px solid #e9ecef;
        margin-bottom: 16px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-blue { background: #e7f1ff; color: #0d6efd; }
    .badge-green { background: #d1e7dd; color: #0f5132; }
    .badge-amber { background: #fff3cd; color: #664d03; }
    .flow-step {
        background: #ffffff;
        border-left: 4px solid #0d6efd;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .metric-box {
        text-align: center;
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ Secure Image Steganography</h1>
    <p>Computer Network Security (CNS) Mini Project — Multi-Layer Protection via <strong>AES-256-GCM Authenticated Encryption</strong> and <strong>LSB Spatial Data Hiding</strong></p>
</div>
""", unsafe_allow_html=True)

# Sidebar: Quick Navigation & Project Metadata
with st.sidebar:
    st.image("https://img.shields.io/badge/Security-AES--256--GCM-blue?style=for-the-badge&logo=shield", use_container_width=True)
    st.image("https://img.shields.io/badge/Steganography-LSB_24bit_RGB-success?style=for-the-badge", use_container_width=True)
    st.image("https://img.shields.io/badge/Integrity-SHA--256-orange?style=for-the-badge", use_container_width=True)

    st.markdown("---")
    st.subheader("👥 Project Team")
    st.markdown("""
    **College CNS Mini Project**
    - **Team Size**: 2 Members
    - **Member 1**: Cryptography & Key Derivation (AES-GCM, PBKDF2, SHA-256)
    - **Member 2**: Steganography & UI Integration (LSB Embedding, PIL, Streamlit)
    """)

    st.markdown("---")
    st.subheader("💡 Core Principle")
    st.info("""
    **Cryptography** scrambles the message so it cannot be read without the key.
    
    **Steganography** conceals the existence of the message so an eavesdropper does not even suspect communication is occurring.
    
    *Together, they provide Defense-in-Depth.*
    """)

    # Quick test sample loader
    st.markdown("---")
    st.subheader("📁 Sample Cover Images")
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_images")
    if os.path.exists(sample_dir):
        sample_files = [f for f in os.listdir(sample_dir) if f.endswith(".png")]
        if sample_files:
            selected_sample = st.selectbox("Select sample to preview:", sample_files)
            if selected_sample:
                sample_img_path = os.path.join(sample_dir, selected_sample)
                st.image(sample_img_path, caption=selected_sample, use_container_width=True)

# Main Navigation Tabs
tab_hide, tab_extract, tab_how_it_works, tab_viva = st.tabs([
    "🔒 Hide Message (Embedding)",
    "🔓 Extract Message (Extraction)",
    "ℹ️ How It Works & Architecture",
    "🎓 Viva & CNS Reference"
])

# ==============================================================================
# TAB 1: HIDE MESSAGE
# ==============================================================================
with tab_hide:
    st.header("Step 1: Embed Secret Message into Cover Image")
    st.markdown("Upload a cover image, supply your confidential message and password. The system will encrypt it via **AES-256-GCM** and hide it in the **Least Significant Bits (LSB)**.")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Cover Image Upload")
        uploaded_cover = st.file_uploader(
            "Choose a Cover Image (PNG recommended, lossless required)",
            type=["png", "bmp", "jpg", "jpeg"],
            key="cover_uploader"
        )

        cover_img = None
        if uploaded_cover is not None:
            try:
                cover_img = Image.open(uploaded_cover)
                st.image(cover_img, caption=f"Uploaded Image: {uploaded_cover.name} ({cover_img.size[0]}x{cover_img.size[1]}, {cover_img.mode})", use_container_width=True)
                
                # Check format warning
                if uploaded_cover.type in ["image/jpeg", "image/jpg"]:
                    st.warning("⚠️ JPEG is a lossy format. The system will automatically convert it to lossless RGB PNG for stego output to prevent LSB data loss.")

                # Capacity calculation
                cap = calculate_capacity(cover_img)
                st.markdown(f"""
                <div class="stCard">
                    <strong>Carrier Capacity Statistics:</strong><br>
                    • Dimensions: <code>{cap['width']} × {cap['height']}</code> ({cap['total_pixels']:,} pixels)<br>
                    • Channels: <code>3 (Red, Green, Blue)</code><br>
                    • Total Available Bits: <code>{cap['carrier_bits']:,} bits</code><br>
                    • Maximum Payload: <strong>{cap['max_payload_bytes']:,} bytes ({cap['max_payload_kb']} KB)</strong>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error opening image: {str(e)}")

    with col2:
        st.subheader("2. Secret Data & Security Credentials")
        secret_message = st.text_area(
            "Enter Secret Plaintext Message:",
            placeholder="Type your sensitive data here (e.g. passwords, coordinates, confidential memos)...",
            height=130
        )

        password = st.text_input(
            "Enter Secret Passphrase:",
            type="password",
            placeholder="A strong password for AES-256 key derivation",
            help="Password is never stored. PBKDF2 derives a 256-bit key using HMAC-SHA256 with 100,000 rounds."
        )

        confirm_pwd = st.text_input(
            "Confirm Secret Passphrase:",
            type="password",
            placeholder="Re-enter your password to prevent typo lockouts"
        )

        show_preview = st.checkbox("Preview secret message in plaintext before embedding", value=False)
        if show_preview and secret_message:
            st.info(f"**Plaintext Preview:** `{secret_message}`")

        # Validation status
        ready_to_embed = False
        if cover_img and secret_message and password:
            if password != confirm_pwd:
                st.error("Passwords do not match. Please verify your passphrase.")
            else:
                ready_to_embed = True

        embed_button = st.button("🔒 Encrypt Message & Embed in Image", type="primary", disabled=not ready_to_embed, use_container_width=True)

    # Process Embedding
    if embed_button and cover_img and secret_message and password:
        with st.spinner("Encrypting with AES-256-GCM and embedding into pixel LSBs..."):
            try:
                # 1. Encrypt and package
                payload, meta = encrypt_message(secret_message, password)

                # 2. Embed into image
                stego_img = embed_data(cover_img, payload)

                # 3. Calculate objective quality metrics
                metrics = compute_image_metrics(cover_img, stego_img)

                st.success("✅ Message successfully encrypted and hidden inside the stego image!")

                # Results Section
                res_col1, res_col2 = st.columns([1, 1], gap="large")

                with res_col1:
                    st.subheader("Stego Image (Visual Output)")
                    st.image(stego_img, caption="Stego Image (Contains Hidden AES-256 Ciphertext)", use_container_width=True)

                    # Export as PNG
                    buf = io.BytesIO()
                    stego_img.save(buf, format="PNG")
                    stego_bytes = buf.getvalue()

                    st.download_button(
                        label="⬇️ Download Stego Image (Lossless PNG)",
                        data=stego_bytes,
                        file_name="stego_image.png",
                        mime="image/png",
                        type="primary",
                        use_container_width=True
                    )
                    st.caption("ℹ️ Always save as PNG. Do NOT convert to JPEG, as JPEG lossy compression destroys LSB data.")

                with res_col2:
                    st.subheader("📊 Security & Quality Telemetry")
                    
                    # Cryptographic Telemetry
                    st.markdown(f"""
                    <div class="stCard">
                        <strong>Cryptographic Manifest:</strong><br>
                        • Algorithm: <span class="badge-pill badge-blue">AES-256-GCM</span><br>
                        • Key Derivation: <span class="badge-pill badge-blue">PBKDF2 ({meta['iterations']:,} iter)</span><br>
                        • Random Salt (16B): <code>{meta['salt_hex'][:16]}...</code><br>
                        • Nonce / IV (12B): <code>{meta['nonce_hex']}</code><br>
                        • Auth Tag (16B): <code>{meta['tag_hex']}</code><br>
                        • SHA-256 Checksum: <code>{meta['sha256_hex'][:32]}...</code><br>
                        • Ciphertext Size: <strong>{meta['ciphertext_len']} bytes</strong><br>
                        • Total Payload: <strong>{meta['payload_total_bytes']} bytes</strong>
                    </div>
                    """, unsafe_allow_html=True)

                    # Steganographic Metrics
                    cap_used = (meta['payload_total_bytes'] + 4) / calculate_capacity(cover_img)['carrier_bytes'] * 100
                    st.markdown(f"""
                    <div class="stCard">
                        <strong>Steganographic Imperceptibility Metrics:</strong><br>
                        • Capacity Utilized: <strong>{cap_used:.4f}%</strong><br>
                        • Mean Squared Error (MSE): <strong>{metrics['mse']}</strong> (ideal ≈ 0.0)<br>
                        • Peak Signal-to-Noise Ratio (PSNR): <strong>{metrics['psnr_db']} dB</strong> (academic threshold > 30 dB)<br>
                        <small style="color: green;">✓ PSNR > 50 dB confirms visual indistinguishability to the human visual system (HVS).</small>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Embedding failed: {str(e)}")


# ==============================================================================
# TAB 2: EXTRACT MESSAGE
# ==============================================================================
with tab_extract:
    st.header("Step 2: Extract & Decrypt Secret Message")
    st.markdown("Upload a stego image generated by this application, supply the secret password, and click **Extract & Decrypt**.")

    ext_col1, ext_col2 = st.columns([1, 1], gap="large")

    with ext_col1:
        st.subheader("1. Stego Image Upload")
        uploaded_stego = st.file_uploader(
            "Upload Stego Image (PNG)",
            type=["png", "bmp"],
            key="stego_uploader"
        )

        stego_loaded_img = None
        if uploaded_stego is not None:
            try:
                stego_loaded_img = Image.open(uploaded_stego)
                st.image(stego_loaded_img, caption=f"Stego Image: {uploaded_stego.name} ({stego_loaded_img.size[0]}x{stego_loaded_img.size[1]})", use_container_width=True)
            except Exception as e:
                st.error(f"Failed to load image: {str(e)}")

    with ext_col2:
        st.subheader("2. Decryption Credentials")
        decrypt_pwd = st.text_input(
            "Enter Secret Passphrase for Decryption:",
            type="password",
            placeholder="Passphrase used during embedding",
            key="decrypt_pwd_input"
        )

        extract_button = st.button("🔓 Extract & Decrypt Message", type="primary", disabled=not (stego_loaded_img and decrypt_pwd), use_container_width=True)

    if extract_button and stego_loaded_img and decrypt_pwd:
        with st.spinner("Extracting LSB bitstream and authenticating with AES-256-GCM..."):
            try:
                # Step 1: LSB Extraction
                extracted_payload = extract_data(stego_loaded_img)

                # Step 2: Decrypt & Verify
                decryption_result = decrypt_message(extracted_payload, decrypt_pwd)

                if decryption_result["success"]:
                    st.success("🎉 Authentication & Decryption Successful!")

                    st.markdown("### 📜 Recovered Secret Message:")
                    st.text_area(
                        "Decrypted Message Plaintext:",
                        value=decryption_result["message"],
                        height=140,
                        disabled=True
                    )

                    st.markdown("### 🛡️ Multi-Layer Security Verification:")
                    vcol1, vcol2, vcol3 = st.columns(3)
                    with vcol1:
                        st.markdown("""
                        <div class="metric-box">
                            <span class="badge-pill badge-green">VERIFIED</span><br>
                            <strong>Magic Header</strong><br>
                            <small>Valid stego payload signature</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with vcol2:
                        st.markdown("""
                        <div class="metric-box">
                            <span class="badge-pill badge-green">VALID</span><br>
                            <strong>AES-GCM Auth Tag</strong><br>
                            <small>128-bit integrity check passed</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with vcol3:
                        st.markdown("""
                        <div class="metric-box">
                            <span class="badge-pill badge-green">MATCHED</span><br>
                            <strong>SHA-256 Digest</strong><br>
                            <small>Plaintext hash confirmed</small>
                        </div>
                        """, unsafe_allow_html=True)

                    with st.expander("🔍 View Technical Cryptographic Parameters"):
                        meta = decryption_result["metadata"]
                        st.json({
                            "Salt Hex": meta.get("salt_hex"),
                            "Nonce Hex": meta.get("nonce_hex"),
                            "Auth Tag Hex": meta.get("tag_hex"),
                            "Expected SHA-256": meta.get("expected_sha256"),
                            "Actual SHA-256": meta.get("actual_sha256"),
                            "Ciphertext Bytes": meta.get("ciphertext_len")
                        })

                else:
                    st.error(f"❌ Decryption Failed: {decryption_result['error']}")
                    
                    st.markdown("### ⚠️ Security Diagnostic:")
                    st.markdown("""
                    Possible reasons for failure:
                    1. **Incorrect Password**: AES-256-GCM authenticated encryption will reject even a 1-character typo with 100% certainty.
                    2. **Modified or Corrupted Image**: Any compression (like JPEG saving) or image filtering flips pixel LSBs, invalidating the GCM authentication tag.
                    3. **Plain Cover Image**: The uploaded image does not contain data embedded by this system.
                    """)

            except ValueError as ve:
                st.error(f"❌ Steganography Extraction Error: {str(ve)}")
                st.info("The image does not contain valid steganographic data or the header was destroyed.")
            except Exception as ex:
                st.error(f"❌ Unexpected Error: {str(ex)}")


# ==============================================================================
# TAB 3: HOW IT WORKS & ARCHITECTURE
# ==============================================================================
with tab_how_it_works:
    st.header("System Architecture & Security Workflow")

    st.markdown("""
    This project unites two core pillars of information security:
    - **Cryptography (AES-256-GCM)** ensures that the message is mathematically incomprehensible to anyone without the secret key.
    - **Steganography (LSB Data Hiding)** ensures that third parties are unaware that any secret message even exists.
    """)

    arch_col1, arch_col2 = st.columns(2, gap="large")

    with arch_col1:
        st.subheader("🔒 Embedding Flow (Sender)")
        st.markdown("""
        <div class="flow-step">
            <strong>1. Plaintext Message</strong><br>
            User enters secret text. The system computes a 256-bit SHA-256 hash for end-to-end integrity auditing.
        </div>
        <div class="flow-step">
            <strong>2. Key Derivation (PBKDF2)</strong><br>
            A 16-byte random salt is generated. PBKDF2 executes 100,000 rounds of HMAC-SHA256 on the password to derive a 256-bit AES key.
        </div>
        <div class="flow-step">
            <strong>3. AES-256-GCM Encryption</strong><br>
            A 12-byte random nonce is created. AES in Galois/Counter Mode encrypts the plaintext and produces ciphertext + a 16-byte authentication tag.
        </div>
        <div class="flow-step">
            <strong>4. Payload Serialization</strong><br>
            <code>[Magic: 'STEG' (4B)] + [Salt (16B)] + [Nonce (12B)] + [Tag (16B)] + [SHA256 (32B)] + [CT_Len (4B)] + [Ciphertext]</code>
        </div>
        <div class="flow-step">
            <strong>5. LSB Spatial Insertion</strong><br>
            Bits are embedded into the 0th bit of Red, Green, and Blue channels of the cover image. The result is saved as lossless PNG.
        </div>
        """, unsafe_allow_html=True)

    with arch_col2:
        st.subheader("🔓 Extraction Flow (Receiver)")
        st.markdown("""
        <div class="flow-step">
            <strong>1. Stego Image Input</strong><br>
            Receiver supplies the stego PNG file and the shared passphrase.
        </div>
        <div class="flow-step">
            <strong>2. LSB Bitstream Extraction</strong><br>
            The system reads the 32-bit payload length prefix and extracts the embedded byte stream from pixel channel LSBs.
        </div>
        <div class="flow-step">
            <strong>3. Signature Verification</strong><br>
            Confirms the <code>'STEG'</code> magic identifier. If missing, terminates immediately.
        </div>
        <div class="flow-step">
            <strong>4. AES-256-GCM Decryption & Tag Check</strong><br>
            Passphrase + extracted Salt derives the AES key via PBKDF2. GCM decrypts ciphertext and checks the 16-byte auth tag. If incorrect password or tampered data, halts.
        </div>
        <div class="flow-step">
            <strong>5. SHA-256 Hash Matching</strong><br>
            Computes SHA-256 of decrypted plaintext and verifies it against the embedded hash. Displays original plaintext.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔬 Technical Deep-Dive: Bitwise LSB Mechanism")
    st.markdown("""
    In a standard 24-bit RGB pixel, each color component has 8 bits (range 0 to 255):
    ```
    Original Pixel Channel Byte : 1 0 1 1 0 1 1 0  (Value = 182)
    Clear LSB with mask 0xFE    : 1 0 1 1 0 1 1 0 & 1 1 1 1 1 1 1 0 -> 1 0 1 1 0 1 1 0
    Secret bit to hide          : 1
    Resulting Stego Channel     : 1 0 1 1 0 1 1 1  (Value = 183)
    Difference                  : +1 intensity unit (Human eye cannot detect this change!)
    ```
    """)

    st.markdown("---")
    st.subheader("⚠️ Why PNG over JPEG? (Crucial Viva Point)")
    st.info("""
    - **PNG (Portable Network Graphics)** uses lossless DEFLATE compression. Every pixel bit stored is recovered bit-for-bit upon decompression.
    - **JPEG (Joint Photographic Experts Group)** uses lossy Discrete Cosine Transform (DCT) compression and quantization. It slightly modifies pixel values to save storage space, which obliterates the least significant bits and destroys steganographic payloads.
    """)


# ==============================================================================
# TAB 4: VIVA & CNS REFERENCE
# ==============================================================================
with tab_viva:
    st.header("🎓 Academic Viva Guide & Project Defense")

    st.subheader("📋 2-Member Team Division of Work")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
        <div class="stCard">
            <h4>Member 1: Cryptography & Security Engineering</h4>
            <ul>
                <li>Implementation of <strong>AES-256-GCM</strong> authenticated encryption.</li>
                <li>Design of <strong>PBKDF2 key derivation</strong> with random 16-byte salt (100k rounds).</li>
                <li>Implementation of <strong>SHA-256</strong> hashing for dual-layer message integrity.</li>
                <li>Packaging of binary header format (Magic, Salt, Nonce, Tag, SHA-256).</li>
                <li>Security analysis against replay attacks and brute-force attacks.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
        <div class="stCard">
            <h4>Member 2: Steganography & Application UI</h4>
            <ul>
                <li>Implementation of <strong>24-bit RGB LSB</strong> embedding and extraction algorithms.</li>
                <li>Image capacity verification and boundary checks using Pillow & NumPy.</li>
                <li>Calculation of image quality metrics (<strong>MSE and PSNR</strong>).</li>
                <li>Development of the <strong>Streamlit</strong> web interface and workflows.</li>
                <li>Format handling and testing lossless PNG integrity.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("❓ Top Viva Questions & Answers")

    vivas = [
        ("Q1: What is the fundamental difference between Cryptography and Steganography?",
         "Cryptography protects the confidentiality of data by converting plaintext into unreadable ciphertext. Steganography conceals the very existence of the message by hiding it inside an innocuous carrier medium (such as an image). Cryptography makes data secret; steganography makes data invisible."),
        
        ("Q2: Why combine AES-256 with LSB steganography in this project?",
         "This provides 'Defense-in-Depth'. If an adversary discovers the steganographic carrier (steganalysis), they cannot read the secret data because it is encrypted with military-grade AES-256. Conversely, if encrypted data was sent in the open, it would immediately attract suspicion; hiding it in an image conceals the transmission."),
        
        ("Q3: Why use AES-GCM mode instead of AES-CBC or AES-ECB?",
         "AES-ECB does not use an IV and reveals data patterns (e.g. ECB penguin). AES-CBC provides confidentiality but not authenticity (vulnerable to padding oracle attacks). AES-GCM (Galois/Counter Mode) is an AEAD (Authenticated Encryption with Associated Data) scheme that simultaneously provides high-speed confidentiality AND a 128-bit authentication tag to immediately detect tampering or incorrect passwords."),
        
        ("Q4: Why is PBKDF2 needed instead of using the user's password directly?",
         "Passwords vary in length and have low entropy (predictable characters). AES-256 strictly requires an exact 256-bit (32-byte) pseudo-random key. PBKDF2 stretches the password through 100,000 iterations of HMAC-SHA256, adding a random 16-byte salt to thwart rainbow table and dictionary attacks."),
        
        ("Q5: What is the purpose of the 16-byte Salt and 12-byte Nonce?",
         "The Salt ensures that two identical passwords produce completely different AES keys. The Nonce (Number used Once) ensures that encrypting the exact same message with the same key produces completely different ciphertexts, preventing replay and pattern-frequency attacks."),
        
        ("Q6: How does LSB data hiding work and why is it imperceptible?",
         "Each 24-bit RGB pixel consists of Red, Green, and Blue bytes (0-255). By replacing only bit 0 (the least significant bit), pixel color values change by at most ±1 unit. The human visual system (HVS) cannot distinguish an intensity change of 1/256 (approx 0.39%), preserving visual imperceptibility."),
        
        ("Q7: What are MSE and PSNR, and what do your project results show?",
         "MSE (Mean Squared Error) measures the average squared difference between original and stego pixels. PSNR (Peak Signal-to-Noise Ratio) is a logarithmic ratio (in dB) between maximum pixel power and distortion noise. A PSNR above 30-40 dB indicates high visual fidelity. In our project, PSNR exceeds 50 dB, proving mathematical imperceptibility."),
        
        ("Q8: Why does saving as JPEG destroy the stego data?",
         "JPEG uses lossy compression involving Discrete Cosine Transform (DCT), quantization, and high-frequency rounding. This alters individual pixel values upon saving, corrupting the delicate least significant bits. PNG uses lossless DEFLATE compression, preserving every bit perfectly."),
        
        ("Q9: What is Kerckhoffs's Principle and how does this project uphold it?",
         "Kerckhoffs's Principle states that a cryptosystem should remain secure even if everything about the system (except the key) is public knowledge. In this project, the embedding algorithm, header structure, and code are completely open; the security depends strictly on the confidentiality of the passphrase and the strength of AES-256."),
        
        ("Q10: What is Steganalysis and how can an attacker detect LSB hiding?",
         "Steganalysis is the science of detecting hidden messages. Simple LSB embedding can be detected using statistical steganalysis such as Chi-square (χ²) analysis, RS (Regular/Singular) analysis, or histogram pair-of-values analysis, which look for anomalies in bit distribution.")
    ]

    for q, a in vivas:
        with st.expander(q):
            st.write(a)
