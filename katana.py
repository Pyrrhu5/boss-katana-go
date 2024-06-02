# import asyncio
# from bleak import BleakScanner
# import os

# os.environ["BLEAK_LOGGING"] = "1"


# async def scan():
#     devices = await BleakScanner.discover()
#     for d in devices:
#         if "MIDI" in d.name:
#             print(f"{d.address=} {d.name=} {d.details=}")
#             return d


# import asyncio
# from bleak import BleakClient
# from uuid import UUID

# address = ":CB:4E:FD:78:76:EF:"
# MODEL_NBR_UUID = "2A24"


# async def on_message(*args):
#     print(*args)


# async def main(address):
#     async with BleakClient(address) as client:
#         services = await client.get_services()
#         service = services.services[1]
#         # service.uuid is 16 bytes, meaning it's a standard protocol
#         # See https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt#services-640991
#         # The UUID correspond to the MIDI protocol (duh)
#         # See the specs
#         # https://hangar42.nl/wp-content/uploads/2017/10/BLE-MIDI-spec.pdf
#         # std bluetooth characteristics: https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/
#         characteristic = service.characteristics[0]
#         descriptor = characteristic.descriptors[0]
#         char_val = await client.read_gatt_char(characteristic)
#         print(char_val)
#         await client.write_gatt_char(characteristic, b"\x01\x00", response=False)
#         char_val = await client.read_gatt_char(characteristic)
#         print(char_val)
#         desc_val = await client.read_gatt_descriptor(descriptor.handle)
#         print(desc_val)
#         # await client.write_gatt_descriptor(descriptor.handle, b"\x00\x01")
#         # desc_val = await client.read_gatt_descriptor(descriptor.handle)
#         # print(desc_val)
#         # print(
#         #     f"{service.uuid=} {characteristic.uuid=} {characteristic.properties=} {characteristic.max_write_without_response_size=}"
#         # )
#         # print("LISTENING")
#         # client.start_notify(characteristic, on_message)
#         # await asyncio.sleep(15.0)
#         # await client.stop_notify(characteristic)
#         # while True:
#         #     out = await client.read_gatt_descriptor(descriptor.handle)
#         # await client.start_notify(characteristic, on_message)

#         # print(out)
#         # model_number = await client.read_gatt_char(service.uuid)
#         # print("Model Number: {0}".format("".join(map(chr, model_number))))


# katana = asyncio.run(scan())
# asyncio.run(main(katana.address))

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

