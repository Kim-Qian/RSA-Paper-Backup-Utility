# 🔐 RSA Paper Backup Utility

> Secure offline paper backup & recovery tool for RSA private keys

---

## 📌 Introduction / 项目简介

**RSA Paper Backup Utility** is an offline desktop application that converts RSA private keys (PEM format) into printable paper backups containing:

- Raw key text
- Cryptographic fingerprint (SHA-256)
- High-density QR code (compressed & encoded)

The QR code can later be scanned via camera to fully restore the original PEM file with integrity verification.

**RSA Paper Backup Utility** 是一个完全离线的桌面应用，用于将 RSA 私钥（PEM 格式）转换为**纸质备份**，并在需要时通过扫描二维码恢复私钥文件，同时验证数据完整性。

---

## ✨ Features / 功能特性

### 🔒 Security-Oriented Design / 安全设计
- No network access required（完全离线）
- Gzip compression + Base64 encoding
- SHA-256 fingerprint for manual verification
- No cloud storage, no telemetry

### 🖨️ Paper Backup Generation / 纸质备份生成
- Convert PEM private key to professional PDF
- Includes:
  - Full PEM content
  - Generation timestamp
  - SHA-256 fingerprint
  - User annotations
  - High-density QR code

### 📷 Recovery via Camera / 摄像头恢复
- Scan QR code directly from printed paper
- Automatic decompression and decoding
- Fingerprint verification before saving
- Manual confirmation required

### 🖥️ Modern UI / 现代界面
- Built with CustomTkinter
- Dark mode UI
- Tab-based workflow
- Real-time camera preview

---

## 🧠 How It Works / 工作原理

### Backup Process / 备份流程

1. Load RSA private key (`.pem`)
2. Compress using `gzip`
3. Encode using `Base64`
4. Generate QR code
5. Embed QR + metadata into PDF
6. Print and store securely

### Restore Process / 恢复流程

1. Scan QR code using camera
2. Decode Base64 payload
3. Decompress gzip data
4. Reconstruct PEM file
5. Calculate SHA-256 fingerprint
6. User verifies fingerprint
7. Save restored key

---

## 📂 Output Format / 输出内容

**PDF includes:**

- RSA private key (raw text)
- File name
- Generation timestamp
- SHA-256 fingerprint
- User annotations
- Centered QR code for recovery

---

## 🧰 Dependencies / 依赖库

```bash
pip install customtkinter
pip install opencv-python
pip install qrcode
pip install pillow
pip install pyzbar
pip install reportlab
pip install numpy

⚠️ On Windows, pyzbar requires zbar installed.

---

## ▶️ Usage / 使用方法
python main.py

Generate Backup / 生成备份

Open Generate Backup tab

Select PEM file

(Optional) Add annotations

Save as PDF

Print and store securely

Restore from Paper / 从纸质恢复

Open Restore from Paper tab

Start camera

Scan QR code

Verify fingerprint manually

Save restored PEM file

## ⚠️ Security Notes / 安全提示

Treat printed paper backups as highly sensitive

Store in secure physical locations

Do NOT photograph or digitize printed backups

Destroy paper securely if no longer needed

Anyone with QR code can fully restore the key

## 🧪 Intended Use Cases / 适用场景

Cold storage of RSA private keys

Disaster recovery

Long-term archival

Offline key escrow

Air-gapped environments

## 📜 License / 许可证

MIT License

## 🧑‍💻 Author

Designed & developed by Kim Qian
