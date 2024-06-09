"""Not really automated testing. But has to manually asses if the commands have been sent."""
from time import sleep

from katana_go import LOGGER
from katana_go.config import Config
from katana_go.connection import Bluetooth
from katana_go.roland_midi import create_katana_packet, start_sequence
from katana_go.roland_sysex import Parameter, ParameterValue, roland_sysex

def setup():
    config = Config()
    connection = Bluetooth.cli(config)

    return connection


def _simple_parameters_test(connection, parameter: Parameter, parameter_config: ParameterValue):
    for value in [parameter_config.max_value, parameter_config.min_value, parameter_config.max_value//2]:
        LOGGER.info(f"Testing {parameter.__class__.__name__} {parameter_config} at value {value}")
        packet = create_katana_packet(parameter, parameter_config, value)
        if connection:
            connection.send(packet)
            sleep(5)

def test_amp(connection):
    for parameter in [roland_sysex.amp]:
        for parameter_name, parameter_config in {
            "volume":parameter.volume,
            "gain": parameter.gain,
            "bass": parameter.bass,
            "middle": parameter.middle,
            "treble": parameter.treble,
            "amp_presence": parameter.presence,
            "amp_selection": parameter.amp_selection,
            "amp_variation": parameter.amp_variation,
            "cab_resonance": parameter.cab_resonance,
        }.items():
            LOGGER.info(f"**** Testing {parameter_name.upper()}")
            _simple_parameters_test(connection, parameter, parameter_config)

def test_presets(connection):
    LOGGER.info("**** Testing PRESETS")
    _simple_parameters_test(connection, roland_sysex.preset_select, roland_sysex.preset_select)

def test_all(connection):
    test_amp(connection)
    test_presets(connection)


if __name__ == "__main__":
    connection = setup()
    for p in start_sequence():
        connection.send(p)
    sleep(5)
    test_all(connection)
