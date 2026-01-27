# ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import rtmidi


class BridgeUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Serial-MIDI Bridge")

        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        self._build()
        self.scan_ports()

    def _build(self):
        self.serial_var = tk.StringVar()
        self.baud_var = tk.IntVar(value=31250)
        self.midi_in_var = tk.StringVar()
        self.midi_out_var = tk.StringVar()

        ttk.Label(self.root, text="Serial Port").grid(row=0, column=0, sticky="w")
        self.serial_cb = ttk.Combobox(self.root, textvariable=self.serial_var, width=40)
        self.serial_cb.grid(row=0, column=1)

        ttk.Label(self.root, text="Baudrate").grid(row=1, column=0, sticky="w")
        self.baud_cb = ttk.Combobox(
            self.root,
            values=[9600, 19200, 31250, 57600, 115200],
            textvariable=self.baud_var,
        )
        self.baud_cb.grid(row=1, column=1)

        ttk.Label(self.root, text="MIDI In").grid(row=2, column=0, sticky="w")
        self.midi_in_cb = ttk.Combobox(self.root, textvariable=self.midi_in_var, width=40)
        self.midi_in_cb.grid(row=2, column=1)

        ttk.Label(self.root, text="MIDI Out").grid(row=3, column=0, sticky="w")
        self.midi_out_cb = ttk.Combobox(self.root, textvariable=self.midi_out_var, width=40)
        self.midi_out_cb.grid(row=3, column=1)

        self.start_btn = ttk.Button(self.root, text="Start")
        self.start_btn.grid(row=4, column=0)

        self.scan_btn = ttk.Button(self.root, text="Scan")
        self.scan_btn.grid(row=4, column=1)

        self.exit_btn = ttk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_btn.grid(row=4, column=2)

    def scan_ports(self):
        serial_ports = [p.device for p in serial.tools.list_ports.comports()]
        self.serial_cb["values"] = serial_ports

        self.midi_in_ports = self.midi_in.get_ports()
        self.midi_out_ports = self.midi_out.get_ports()

        self.midi_in_cb["values"] = self.midi_in_ports
        self.midi_out_cb["values"] = self.midi_out_ports

    def run(self):
        self.root.mainloop()
