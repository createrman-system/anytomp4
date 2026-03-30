# 🎬 AnyToMP4

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)  
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)  

**AnyToMP4** is a powerful and user-friendly Python tool with a modern GUI for **encoding any file into MP4** and decoding it back securely. It includes optional encryption support and is perfect for both CLI enthusiasts and GUI users.

---

## ✨ Key Features

- 🔹 Encode **any file type** into MP4 videos
- 🔹 Decode MP4 videos back to original files
- 🔹 Optional **encryption key** for secure storage
- 🔹 Intuitive **drag & drop GUI** with modern blue theme
- 🔹 Real-time logs in GUI console
- 🔹 CLI support for automation and scripting
- 🔹 Cross-platform support: Windows, Linux, macOS

---

## 📦 Installation

### 1️⃣ CLI Dependencies
```bash
pip install opencv-python numpy
```

### 2️⃣ GUI Dependencies
```bash
pip install customtkinter tkinterdnd2
```

> 💡 `tkinter` is included with Python by default.

---

## 💻 Command-Line Usage

### Encode a file
```bash
python coder.py encode FILENAME.xxx FILENAME.mp4
```
- `.xxx` → original file extension
- Both files should be in the **same folder as `coder.py`**

### Decode a file
```bash
python coder.py decode FILENAME.mp4
```

---

## 🔑 Encryption Key

1. Create a file named `key.txt` in the same folder as `coder.py`
2. Write your **custom encryption key** inside it (any length)

> Files encoded with a key will **only decode successfully with the correct key**.

---

## 🖥️ GUI Usage

1. Run `gui.py` (or your GUI script)
2. Drag & drop files or use the **Browse** buttons
3. Toggle between **Encode** and **Decode** modes
4. Set output path for encoding (optional for decoding)
5. Press **START** to begin processing
6. Monitor progress and logs in the built-in console

> 🚀 The GUI automatically disables the START button during processing to prevent accidental multiple runs.

---

## ⚡ Notes

- Supports **all file types**
- GUI features a **clean, modern blue theme**
- MP4 files are **encrypted** if `key.txt` exists
- Perfect for personal use, automation, and scripting
- Designed to be **cross-platform and easy-to-use**

---

## 📖 Suggested Workflow

1. Prepare `key.txt` for encryption (optional)
2. Encode your files using CLI or GUI
3. Store MP4 files securely
4. Decode anytime using the correct key

---

