# midi_parser.py
from typing import List, Optional

CHANNEL_MESSAGE_LENGTHS = {
    0x80: 3,
    0x90: 3,
    0xA0: 3,
    0xB0: 3,
    0xC0: 2,
    0xD0: 2,
    0xE0: 3,
}

SYSTEM_MESSAGE_LENGTHS = {
    0xF1: 2,
    0xF2: 3,
    0xF3: 2,
    0xF6: 1,
    0xF8: 1,
    0xFA: 1,
    0xFB: 1,
    0xFC: 1,
    0xFE: 1,
    0xFF: 1,
}


def get_midi_message_length(buffer: List[int]) -> Optional[int]:
    if not buffer:
        return None

    status = buffer[0]

    # SysEx
    if status == 0xF0:
        if 0xF7 in buffer:
            return buffer.index(0xF7) + 1
        return None

    if status & 0xF0 in CHANNEL_MESSAGE_LENGTHS:
        return CHANNEL_MESSAGE_LENGTHS[status & 0xF0]

    return SYSTEM_MESSAGE_LENGTHS.get(status)
