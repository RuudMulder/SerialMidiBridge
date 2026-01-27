# ui.py
import PySimpleGUI as sg
import serial.tools.list_ports
import rtmidi
from config import APP_NAME, FONT


class BridgeUI:
    def __init__(self):
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        self.serial_ports = []
        self.midi_in_ports = []
        self.midi_out_ports = []

        self.window = self._create_window()
        self.scan_ports()

    def _create_window(self):
        layout = [
            [sg.Text("Serial Port"), sg.Combo([], key="-SERIAL-", size=(40, 1))],
            [sg.Text("Baudrate"), sg.Combo([9600, 19200, 31250, 57600, 115200],
                                           default_value=31250, key="-BAUD-")],
            [sg.Text("MIDI In"), sg.Combo([], key="-MIDI-IN-", size=(40, 1))],
            [sg.Text("MIDI Out"), sg.Combo([], key="-MIDI-OUT-", size=(40, 1))],
            [sg.Button("Scan"), sg.Button("Start"), sg.Button("Exit")]
        ]

        return sg.Window(APP_NAME, layout, font=FONT)

    def scan_ports(self):
        self.serial_ports = list(serial.tools.list_ports.comports())
        self.midi_in_ports = self.midi_in.get_ports()
        self.midi_out_ports = self.midi_out.get_ports()

        self.window["-SERIAL-"].update(
            values=[p.device for p in self.serial_ports]
        )
        self.window["-MIDI-IN-"].update(values=self.midi_in_ports)
        self.window["-MIDI-OUT-"].update(values=self.midi_out_ports)

    def read(self):
        return self.window.read()

    def close(self):
        self.window.close()
