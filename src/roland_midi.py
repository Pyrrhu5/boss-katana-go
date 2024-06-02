from functools import partial

from src.ble_midi import create_sysex_packet, bytes_to_hex, get_timestamp
from src import LOGGER
from src.sysex import NonRealTime

_ROLAND_VENDOR_ID = 0x41
_KATANA_DEVICE_ID = 0x10
_KATANA_MODEL_ID = 0x01  # maybe a unique identifier for a generation of GO


def get_checksum(*data):
    checksum = sum(data) % 128
    return (128 - checksum) % 128


def create_katana_packet(*data):
    LOGGER.info(f"Preparing packet for {bytes_to_hex(data)}")
    timestamp = get_timestamp()
    checksum = get_checksum(*data)
    LOGGER.debug(f"Timestamp: {bytes_to_hex([timestamp])}")
    LOGGER.debug(f"Checksum: {bytes_to_hex([checksum])}")

    return create_sysex_packet(
        _ROLAND_VENDOR_ID,
        _KATANA_DEVICE_ID,
        _KATANA_MODEL_ID,
        *[0x05, 0x0D, 0x12],  # TODO
        *data,
        checksum,
        timestamp,
    )


def start_sequence():
    """A serie a packets sent just after connecting."""
    create_packet = partial(
        create_sysex_packet,
        NonRealTime.vendor_id.value,
        _KATANA_DEVICE_ID,
        NonRealTime.general_information.value.identity_request.value,
    )
    return [
        create_packet(value)
        # No idea what these parameters are
        for value in [0x8C, 0x8F, 0x9A, 0x9A, 0xA0, 0x9D, 0xEC]
    ]
