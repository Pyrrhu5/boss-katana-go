"""Roland uses (exclusively?) sysex to command.

References:
    Roland TB-3 Midi implementation: https://cdn.roland.com/assets/media/pdf/TB-3_MI_1.pdf
"""

from functools import partial

from katana_go.ble_midi import create_sysex_packet, bytes_to_hex, get_timestamp
from katana_go import LOGGER
from katana_go.sysex import NonRealTime
from katana_go.roland_sysex import Parameter, ParameterValue

_ROLAND_VENDOR_ID = 0x41
_KATANA_DEVICE_ID = 0x10
_KATANA_MODEL_ID = 0x01  # maybe a unique identifier for a generation of GO


def get_checksum(*data):
    checksum = sum(data) % 128
    return (128 - checksum) % 128


def create_roland_sysex_packet(*data):
    """Create a packet according to Roland specifications for sysex.
    
    For a higher level API use create_katana_packet
    
    References:
        https://cdn.roland.com/assets/media/pdf/TB-3_MI_1.pdf
    """
    LOGGER.info(f"Preparing packet for {bytes_to_hex(data)}")
    timestamp = get_timestamp()
    checksum = get_checksum(*data)
    LOGGER.debug(f"Timestamp: {bytes_to_hex([timestamp])}")
    LOGGER.debug(f"Checksum: {bytes_to_hex([checksum])}")

    packet = create_sysex_packet(
        _ROLAND_VENDOR_ID,
        _KATANA_DEVICE_ID,
        _KATANA_MODEL_ID,
        *[0x05, 0x0D, 0x12],  # TODO what is it?
        *data,
        checksum,
        timestamp,
    )
    LOGGER.debug(f"Packet produced {bytes_to_hex(packet)}")

    return packet


def create_katana_packet(parameter: Parameter, parameter_config: ParameterValue, value: int):
    """High level API to create a Roland sysex packet specifically for the Katana:GO."""
    return create_roland_sysex_packet(
        parameter.parameter_id,
        parameter.parameter_sub_id,
        parameter_config.id,
        parameter_config.value_1,
        value,
        parameter_config.value_2,
    )


def start_sequence():
    """A series a packets sent just after connecting.

    Unsure of their purpose"""
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
