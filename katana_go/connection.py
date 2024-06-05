"""Means to connect to the amp"""

import asyncio
from typing import Optional
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

from katana_go import LOGGER
from katana_go.config import Config


class Bluetooth:

    def __init__(self, address) -> None:
        self.address = address
        self._device: Optional[BLEDevice] = None
        self._client: Optional[BleakClient] = None
        self.is_connected = False
        self._event_loop = asyncio.get_event_loop()

    def send(self, data):
        self._event_loop.run_until_complete(
            self.client.write_gatt_char(
                "7772E5DB-3868-4112-A1A9-F2669D106BF3", bytearray(data), response=False
            )
        )

    @property
    def client(self) -> BleakClient:
        if not self._client:
            self._client = BleakClient(self.address)
        if not self.is_connected:
            LOGGER.info("Connecting to the bluetooth client...")
            self._event_loop.run_until_complete(self._client.connect())
            self.is_connected = True
            LOGGER.debug("Connected to the bluetooth client.")
        return self._client

    @property
    def device(self) -> BLEDevice:
        if not self._device:
            self._device = asyncio.run(self.get_device(self.address))
        return self._device

    @staticmethod
    async def get_device(address, timeout=5):
        return await BleakScanner.find_device_by_address(address, timeout=timeout)

    @staticmethod
    async def scan():
        return await BleakScanner.discover()

    @classmethod
    def cli(cls, config: Config) -> "Bluetooth":
        if not config.is_config_exists():
            devices = asyncio.run(cls.scan())
            message = "Choose a device:\n"
            for index, device in enumerate(devices):
                message += f"[{index}] - {device.name} {device.address}\n"
            device_choosen = input(message)
            address = devices[int(device_choosen)].address
            print(address)
            config.device_bluetooth_address = address
        else:
            address = config.device_bluetooth_address

        instance = cls(address)

        return instance

    def __del__(self):
        if self.is_connected:
            LOGGER.info("Disconnecting from the bluetooth client...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.client.disconnect())
            LOGGER.debug("Disconnected from the bluetooth client.")
