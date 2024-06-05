from time import sleep

from src.connection import Bluetooth
from src.config import Config
from src.roland_midi import create_katana_packet
from src.roland_sysex import roland_sysex


config = Config()
connection = Bluetooth.cli(config)
# volume to max
print("VOLUME MAX")
r = create_katana_packet(
    roland_sysex.patch,
    roland_sysex.patch.volume,
    roland_sysex.patch.volume.max_value
)
connection.send(r)

sleep(5)
print("VOLUME MIN")
# volume to min
r = create_katana_packet(
    roland_sysex.patch,
    roland_sysex.patch.volume,
    roland_sysex.patch.volume.min_value
)
connection.send(r)
sleep(5)

# volume to middle
print("VOLUME MIDDLE")
r = create_katana_packet(
    roland_sysex.patch,
    roland_sysex.patch.volume,
    roland_sysex.patch.volume.max_value // 2
)
connection.send(r)
sleep(1)

# iterate over the presets
for preset_index in range(roland_sysex.preset_select.max_value):
    print("PRESET", preset_index)
    r = create_katana_packet(
        roland_sysex.preset_select,
        roland_sysex.preset_select,
        preset_index
    )
    connection.send(r)
    sleep(1)

