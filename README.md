# Serial MIDI Bridge (Apple Silicon)

A Python application that bridges **Serial (e.g. Arduino / electronic drums)** and **MIDI**, featuring a **Tkinter-based GUI** and full compatibility with **macOS Apple Silicon (M1 / M2 / M3)**.

---

### SerialMidiBridge

This is a replacement for [https://github.com/projectgus/hairless-midiserial](https://github.com/projectgus/hairless-midiserial) that stopped working with OS X Catalina.

It is based on the excellent [serialmidibridge](https://github.com/chava100f/SerialMidiBridge) python script. I just refactored it a bit to make it compatible with Apple Silicon.

### Usage

After starting you will be able to choose the serial port, baudrate, serial-to-midi port and midi-to-serial port. The Scan button will re-scan for available serial and midi ports. Your selection is remembered for next usage. After starting the server no changes can be made until the server is stopped.


## 📦 System Requirements

* macOS 12+ (Monterey or newer)
* **Apple Silicon** processor (M1, M2, M3)
* Python **3.10 or newer** (recommended: 3.11)
* Xcode Command Line Tools

---

## 🐍 Python

Check your Python version:

```bash
python3 --version
```

If needed, install or upgrade Python using **Homebrew**:

```bash
brew install python
```

---

## 🛠 System Dependencies (Required)

Install the native libraries required for MIDI and Serial support:

```bash
brew install portmidi
brew install pkg-config
```

> ⚠️ `portmidi` is required for `python-rtmidi` to work correctly on Apple Silicon.

---

## 📦 Python Dependencies

It is **strongly recommended** to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Upgrade `pip`:

```bash
pip install --upgrade pip
```

Install the required Python packages:

```bash
pip install pyserial python-rtmidi
```

> ❗ **Do NOT use** `--no-binary` on Apple Silicon. Precompiled wheels are available


### Notes

Due to the use of [PySimpleGui](https://pypi.org/project/PySimpleGUI/) there are some cosmetic 'features':

- There is extra space after all texts because the width in characters is set for a non-proportional font.
- After re-scanning for ports it might be that the baudrate selection is not resized.
- When the previously used serial port is not available at startup its name might still be in the selection box.
