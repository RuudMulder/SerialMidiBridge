# bridge.py
import threading
import queue
import logging
import serial
import rtmidi
from typing import Optional, List
from midi_parser import get_midi_message_length

log = logging.getLogger(__name__)


class SerialMidiBridge:
    def __init__(
        self,
        serial_port: str,
        baudrate: int,
        midi_in_index: int,
        midi_out_index: int,
        queue_size: int = 1024,
    ):
        self.serial_port_name = serial_port
        self.baudrate = baudrate

        self.serial: Optional[serial.Serial] = None
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        self.midi_in_index = midi_in_index
        self.midi_out_index = midi_out_index

        self.running = threading.Event()
        self.ready = threading.Event()

        self.to_serial = queue.Queue(maxsize=queue_size)
        self.to_midi = queue.Queue(maxsize=queue_size)

        self.threads: List[threading.Thread] = []

    # ---------- Lifecycle ----------

    def start(self):
        log.info("Starting Serial-MIDI bridge")
        self.serial = serial.Serial(
            self.serial_port_name,
            self.baudrate,
            timeout=0.4,
        )

        self.midi_in.open_port(self.midi_in_index)
        self.midi_out.open_port(self.midi_out_index)

        self.midi_in.ignore_types(sysex=False, timing=False, active_sense=False)
        self.midi_in.set_callback(self._on_midi_input)

        self.running.set()
        self.ready.set()

        self._start_threads()

    def stop(self):
        log.info("Stopping bridge")
        self.running.clear()

        for t in self.threads:
            t.join(timeout=1.0)

        self.ready.clear()

        if self.serial and self.serial.is_open:
            self.serial.close()

        self.midi_in.close_port()
        self.midi_out.close_port()

    # ---------- Threads ----------

    def _start_threads(self):
        self.threads = [
            threading.Thread(target=self._serial_reader, daemon=True),
            threading.Thread(target=self._serial_writer, daemon=True),
            threading.Thread(target=self._midi_writer, daemon=True),
        ]
        for t in self.threads:
            t.start()

    # ---------- MIDI ----------

    def _on_midi_input(self, event, _):
        message, _dt = event
        try:
            self.to_serial.put_nowait(bytes(message))
        except queue.Full:
            log.warning("Serial queue full, dropping MIDI message")

    def _midi_writer(self):
        while self.running.is_set():
            try:
                message = self.to_midi.get(timeout=0.4)
                self.midi_out.send_message(message)
            except queue.Empty:
                continue

    # ---------- Serial ----------

    def _serial_writer(self):
        while self.running.is_set():
            try:
                data = self.to_serial.get(timeout=0.4)
                self.serial.write(data)
            except queue.Empty:
                continue
            except Exception as e:
                log.error("Serial write error: %s", e)

    def _serial_reader(self):
        buffer: List[int] = []

        while self.running.is_set():
            try:
                byte = self.serial.read(1)
                if not byte:
                    continue

                buffer.append(byte[0])
                length = get_midi_message_length(buffer)

                if length and len(buffer) >= length:
                    self.to_midi.put(buffer[:length])
                    buffer = buffer[length:]

            except Exception as e:
                log.error("Serial read error: %s", e)
