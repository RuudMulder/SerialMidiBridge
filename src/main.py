# main.py
import logging
from ui import BridgeUI
from bridge import SerialMidiBridge
from config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)


def main():
    ui = BridgeUI()
    bridge = None

    while True:
        event, values = ui.read()

        if event in (None, "Exit"):
            break

        if event == "Scan":
            ui.scan_ports()

        if event == "Start":
            if bridge:
                bridge.stop()
                bridge = None
                ui.window["Start"].update("Start")
            else:
                try:
                    serial_port = values["-SERIAL-"]
                    baudrate = int(values["-BAUD-"])
                    midi_in = ui.midi_in_ports.index(values["-MIDI-IN-"])
                    midi_out = ui.midi_out_ports.index(values["-MIDI-OUT-"])

                    bridge = SerialMidiBridge(
                        serial_port,
                        baudrate,
                        midi_in,
                        midi_out,
                    )
                    bridge.start()
                    ui.window["Start"].update("Stop")

                except Exception as e:
                    logging.exception(e)

    if bridge:
        bridge.stop()

    ui.close()


if __name__ == "__main__":
    main()
