"""Implements the MIDI BLE specification to create compatible packets to send to the amp.

Notions:
    MSB: most significant byte
    LSB: least significant byte
    delta_time: time (ms) since the last message, it allows the receiver to order the messages.
    sysex: protocols outside of the specification, defined by a vendor (hence, requires a vendor_id)

References:
    Vendors ID: https://electronicmusic.fandom.com/wiki/List_of_MIDI_Manufacturer_IDs
"""

from src import LOGGER
from time import time


def _generate_header(timestamp: int):
    """Generates the BLE MIDI header byte."""

    # The header byte has the MSB set to 0
    # The remaining 7 bits represents the timestamp
    header_byte = 0x80 | (timestamp & 0x7F)

    return header_byte


def get_timestamp() -> list[int]:
    """Get the current time at the packet format."""

    time_ms = int(time() * 1000)
    # constraint to a 13 bits range
    time_ms = time_ms % 8192
    # Extract the least significant 7 bits and prepend '1'
    lsb = (1 << 7) | (time_ms & 0x7F)

    return lsb


def create_packet(*data) -> list[int]:
    timestamp = get_timestamp()
    header = _generate_header(timestamp)
    return [header] + [timestamp] + list(data)


# As defined by midi.org sysex protocol
PROTOCOL_START_BYTE = 0xF0
PROTOCOL_END_BYTE = 0xF7


def create_sysex_packet(vendor_id: int, device_id: int, model_id: int, *data):
    """Sysex is a free-for-all part of the MIDI protocol where vendors can do whatever they want."""
    return create_packet(
        PROTOCOL_START_BYTE,
        vendor_id,  # defined by midi.org
        device_id,  # defined by the vendor
        model_id,  # whatever the vendor wants
        *data,
        PROTOCOL_END_BYTE,
    )


def bytes_to_hex(bytes_: list[int]):
    """Convert a packet into hex representation, to preserve the dev's eyes."""
    return ":".join(f"{byte:02x}" for byte in bytes_)
