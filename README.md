### SerialMidiBridge

This is a replacement for [https://github.com/projectgus/hairless-midiserial](https://github.com/projectgus/hairless-midiserial) that stopped working with OS X Catalina.

It is based on the excellent [serialmidibridge](https://github.com/chava100f/SerialMidiBridge) python script. I just refactored it a bit to make it compatible with Apple Silicon.

### Usage

After starting you will be able to choose the serial port, baudrate, serial-to-midi port and midi-to-serial port. The Scan button will re-scan for available serial and midi ports. Your selection is remembered for next usage. After starting the server no changes can be made until the server is stopped.

### Starting from the command line

### Required libs (step by step on Mac)

```
brew install python@3.11
```
brew update
brew install rtmidi pkg-config

```
```
pip3 install pyserial
```
```
pip3 install PySimpleGUI
```
In case of graphical issues:
```
brew install python-tk
```

After install dependencies you can install the serial midi bridge using the following command:

```
python3 main.py
```

### Adapting/building

If you want to make changes or build your own application you can use pyinstaller:

```
pyinstaller --onefile --windowed SerialMidiBridge.py
```

N.B. pyinstaller can be installed as follows:

```
pip install pyinstaller
```

You are free to modify it as long as it's not for commercial purposes.

### Notes

Due to the use of [PySimpleGui](https://pypi.org/project/PySimpleGUI/) there are some cosmetic 'features':

- There is extra space after all texts because the width in characters is set for a non-proportional font.
- After re-scanning for ports it might be that the baudrate selection is not resized.
- When the previously used serial port is not available at startup its name might still be in the selection box.
