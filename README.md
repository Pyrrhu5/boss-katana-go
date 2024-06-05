# Katana-go

A package to interact with Boss' Katana:GO amp via bluetooth.

Only implements sending commands to the Katana:GO, not receiving.

## Installation

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage examples

```python
from src.connection import Bluetooth
from src.config import Config
from src.roland_midi import create_katana_packet, create_roland_packet
from src.roland_sysex import roland_sysex

config = Config()
connection = Bluetooth.cli(config)  # Will ask for the device at first run

# Use the highest level interface
# See roland_sysex for the options
print("VOLUME MAX")
r = create_katana_packet(
    roland_sysex.patch,
    roland_sysex.patch.volume,
    roland_sysex.patch.volume.max_value
)
connection.send(r)

# Use the lower level interface
r = create_roland_sysex_packet(
    0x20,  # Parameter ID
    0x00,  # Parameter sub-id
    0x20,  # Command ID
    0x01,  # Value, constant in this case
    0x64,  # Value, volume max
    # Some commands have a third byte
)
connection.send(r)
```

## Reverse-engineering

The MIDI protocol authorizes arbitrary packets, under the SYSEX denomination, so any manufacturer can creates custom commands which are not defined by the MIDI protocol.

Roland went full-in, and even the commands defined by the protocol do not work (really, reimplementing changing the master volume???).

The relevant packets seem to only have 17 or 18 bytes.

The packets have this structure (hex notation):
```
A2:F8:F0:41:10:01:05:0D:12:20:00:20:01:00:50:6F:F8:F7

HEADER:TIMESTAMP:START_BYTE:VENDOR_ID:DEVICE_ID:MODEL_ID:R_UNKNOWN:R_UNKNOWN:R_UNKNOWN:R_PARAMETER_ID:R_PARAMETER_SUBID:CMD_ID:VALUE_1:VALUE_2:VALUE_3:R_CHECKSUM:TIMESTAMP:END_BYTE
```

**MIDI protocol:**

```
HEADER:TIMESTAMP:START_BYTE:VENDOR_ID:DEVICE_ID:MODEL_ID:<SYSEX part>:END_BYTE
```

- `HEADER`: Roland seems to ignore it
- `TIMESTAMP`: Roland reimplement it and seems to ignore this one. Allows the receiver to process the packets in order.
- `START_BYTE`: constant, indicates the beginning of a SYSEX instruction
- `END_BYTE`: constant, indicates the end of a SYSEX instruction
- `VENDOR_ID`: the manufacturer, constant in the case of Roland
- `DEVICE_ID`: defined by the manufacturer, constant in the case of Katana:GO
- `MODEL_ID`: defined by the manufacturer, constant? Or maybe a Katana:GO generation?

**Roland protocol:**

```
R_UNKNOWN:R_UNKNOWN:R_UNKNOWN:R_PARAMETER_ID:R_PARAMETER_SUBID:CMD_ID:VALUE_1:VALUE_2:VALUE_3:R_CHECKSUM:TIMESTAMP
```

- `R_UNKNOWN`: constants, but no idea what it represents
- `R_PARAMETER_ID`: indicates a "category" of commands (for example: "master controls")
- `R_PARAMETER_SUBID`: indicates a "subcategory" of commands. Constants within a R_PARAMETER_ID
- `CMD_ID`: indicates which command within the R_PARAMETER_ID (continuing the previous example, "volume")
- `VALUE_1`: This might be a constant within a CMD_ID, but is sometimes changing, it depends on how vast the options for the command is
- `VALUE_2`: The actual value. For example, in percentages commands (the nobs) it will be from 0 to 100
- `VALUE_3`: only present in 18 bytes packets, probably for commands which have a lot of options (like presets selection)
- `R_CHECKSUM`: A calculated value to ensure the integrity of the SYSEX part
- `TIMESTAMP`: because it was probably too difficult to use the timestamp defined in the MIDI protocol, why not duplicating this information? It has the same value.

### Procedure

Requirements:
- Android phone with Boss app installed and dev mode activated
- Katana:GO
- A computer with Wireshark (for Linux, don't use the Flatpack or Snap versions if you want to use the script) and adb


1. In developer options, toggle `Enable Bluetooth HCI snoop log`
2. In developer options, toggle `USB debugging`
3. Restart the bluetooth
4. Send some command to the Katana via the app. I recommend to leave at least 10 seconds between commands to facilitate the analysis.
5. With the phone connected with USB, run `adb bugreport <filename>` (it's slow)
6. Extract the log from the archive `FS/data/log/bt/btsnoop_hci.log`
7. Either open it with Wireshark or use the script `shark.py` 
   1. If using the script, install the dependencies`pip install pyshark`
   2. Modify it first as there is a lot of hard-coded stuff
8. Go luck, have fun


