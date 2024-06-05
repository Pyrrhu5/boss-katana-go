import json
from pathlib import Path


class Config:
    def __init__(self) -> None:
        self.config_file = Path("config.json")
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self._config = json.load(f)
        else:
            self._config = {}

    def write(self):
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=4)

    def is_config_exists(self):
        return self.config_file.exists()

    @property
    def device_bluetooth_address(self):
        return self._config["device_address"]

    @device_bluetooth_address.setter
    def device_bluetooth_address(self, mac_address):
        self._config["device_address"] = mac_address
        self.write()
