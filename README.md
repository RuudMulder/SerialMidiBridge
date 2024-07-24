### Notification:

The development on this branch has stopped. Development continues (with a more modern GUI that will work on new MacOs versions) on: [https://github.com/chava100f/SerialMidiBridge](https://github.com/chava100f/SerialMidiBridge).

### SerialMidiBridge

This is a replacement for [https://github.com/projectgus/hairless-midiserial](https://github.com/projectgus/hairless-midiserial) that stopped working with OS X Catalina.

It is based on the excellent [serialmidi](https://github.com/raspy135/serialmidi) python script. I just refactored it a bit to be able to add a Gui.

Not as fancy as hairless-midiserial, but it works and is for end-users easier to use than the serialmidi script (I know at least one of them :wink:).

A complete application for OS X can be downloaded from: [SerialMidiBridge.app.zip](https://mega.nz/file/k5skCQqL#Gu-krXfbGkKWxxRzex5TsaKGbu9fc9izKQyb72-ZagA).

It also works on Linux (at least on Lubuntu19). A complete application for Linux can be downloaded from:
[SerialMidiBridgeLinux.zip](https://mega.nz/file/Ug9h1QTB#_gvN7DPf7y9jejG2K-4btN61jieIyUxwtCvAK9iOorQ)

### Usage

After starting you will be able to choose the serial port, baudrate, serial-to-midi port and midi-to-serial port. The Scan button will re-scan for available serial and midi ports. Your selection is remembered for next usage. After starting the server no changes can be made until the server is stopped.

### Starting from the command line

It can also be started in the Terminal after downloading the python script as follows:

```
python3 SerialMidiBridge.py
```

This requires some python extra packages. You can install them as follows:

```
pip install pyserial python-rtmidi pysimplegui
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
