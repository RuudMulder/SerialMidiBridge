# main.py
from ui import BridgeUI
from bridge import SerialMidiBridge
from tkinter import messagebox
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AppController:
    def __init__(self):
        self.ui = BridgeUI()
        self.bridge = None
        self.running = False

        # Bind buttons
        self.ui.start_btn.config(command=self.toggle_bridge)
        self.ui.scan_btn.config(command=self.scan_ports)

        # Window close
        self.ui.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def scan_ports(self):
        try:
            self.ui.scan_ports()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            log.exception(e)

    def toggle_bridge(self):
        if self.running:
            self.stop_bridge()
        else:
            self.start_bridge()

    def start_bridge(self):
        try:
            serial_port = self.ui.serial_var.get()
            baudrate = self.ui.baud_var.get()
            midi_in_name = self.ui.midi_in_var.get()
            midi_out_name = self.ui.midi_out_var.get()

            if not all([serial_port, baudrate, midi_in_name, midi_out_name]):
                messagebox.showwarning(
                    "Missing selection",
                    "Select Serial, Baudrate, MIDI In and MIDI Out.",
                )
                return

            midi_in_index = self.ui.midi_in_ports.index(midi_in_name)
            midi_out_index = self.ui.midi_out_ports.index(midi_out_name)

            self.bridge = SerialMidiBridge(
                serial_port=serial_port,
                baudrate=int(baudrate),
                midi_in_index=midi_in_index,
                midi_out_index=midi_out_index,
            )

            self.bridge.start()
            self.running = True

            self.ui.start_btn.config(text="Stop")
            self.lock_controls(True)

            log.info("Bridge started")

        except Exception as e:
            messagebox.showerror("Start error", str(e))
            log.exception(e)

    def stop_bridge(self):
        try:
            if self.bridge:
                self.bridge.stop()
                self.bridge = None

            self.running = False
            self.ui.start_btn.config(text="Start")
            self.lock_controls(False)

            log.info("Bridge stopped")

        except Exception as e:
            messagebox.showerror("Stop error", str(e))
            log.exception(e)

    def lock_controls(self, locked):
        state = "disabled" if locked else "normal"
        self.ui.serial_cb.config(state=state)
        self.ui.baud_cb.config(state=state)
        self.ui.midi_in_cb.config(state=state)
        self.ui.midi_out_cb.config(state=state)
        self.ui.scan_btn.config(state=state)

    def on_exit(self):
        if self.running:
            if not messagebox.askyesno(
                "Exit",
                "Bridge is running. Exit anyway?"
            ):
                return
            self.stop_bridge()

        self.ui.root.destroy()

    def run(self):
        self.ui.root.mainloop()


def main():
    AppController().run()


if __name__ == "__main__":
    main()
