#!/usr/bin/env python3

"""Parse an android bluetooth sniff file to extract relevant data

Packet structure:
a2:f8:f0:41:10:01:05:0d:12:20:00:20:01:50:6f:f8:f7
HEADER:TIMESTAMP:START_BYTE:VENDOR_ID:DEVICE_ID:MODEL_ID:R_UNKNOWN:R_UNKNOWN:R_UNKNOWN:R_PARAMETER_ID:R_PARAMETER_SUBID:CMD_ID:VALUE_1:VALUE_2:R_CHECKSUM:TIMESTAMP:END_BYTE
"""

from datetime import datetime
from csv import DictWriter
import pyshark
from pyshark.packet.packet import Packet
from pyshark.packet.layers.xml_layer import XmlLayer

# Load the btsnoop_hci.log file
cap = pyshark.FileCapture('./btsnoop_hci.log')

KATANA_MAC = "cb:4e:fd:78:76:ef"
# Extract relevant packets
data = []
layers_types = set()
for packet in cap:
    packet: Packet
    # for some reason, it has +2h from the hour captured
    if packet.sniff_time < datetime(2024, 6, 4, 9, 24) or packet.sniff_time > datetime(2024, 6, 4, 9, 40):
        continue
    source = destination = value = None
    packet_info = {
        "time": packet.sniff_time,
        "source": None,
        "destination": None,
        "packet": None,
        "len_packet": None,
        "R_PARAMETER_ID" : None,
        "R_PARAMETER_SUBID" : None,
        "CMD_ID" : None,
        "VALUE_1" : None,
        "VALUE_2" : None,
        "VALUE_3": None,
        "Action": None
    }
    for layer in packet.layers:
        layer: XmlLayer
        # Filter communication with other devices than Katana
        if layer.layer_name == "bthci_acl":
            if layer.get_field_value("src_bd_addr") != KATANA_MAC and layer.get_field_value("dst_bd_addr") != KATANA_MAC:
                continue
            source = (layer.get_field_value("src_name"), layer.get_field_value("src_bd_addr"))
            destination = (layer.get_field_value("dst_name"), layer.get_field_value("dst_bd_addr"))
        # retrieve the packet
        if layer.layer_name == "btatt":
            value = layer.get_field_value("value")
    if not source or not destination or not value:
        continue 
    packet_info["source"] = source[0]
    packet_info["destination"] = destination[0]
    packet_info["packet"] = value
    packet_bytes = value.split(":")
    packet_info["len_packet"] = len(packet_bytes)
    try:
        packet_info["R_PARAMETER_ID"] = packet_bytes[9]
        packet_info["R_PARAMETER_SUBID"] = packet_bytes[10]
        # Packets under 17 bytes seems irrelevant
        packet_info["CMD_ID"] = packet_bytes[11] if len(packet_bytes) >= 17 else None
        packet_info["VALUE_1"] = packet_bytes[12] if len(packet_bytes) >= 17 else None
        packet_info["VALUE_2"] = packet_bytes[13] if len(packet_bytes) >= 17 else None
        packet_info["VALUE_3"] = packet_bytes[14] if len(packet_bytes) >= 18 else None
    except:
        pass
    data.append(packet_info)

with open("./output.csv", "w") as output_file:
    writer = DictWriter(output_file, fieldnames=packet_info.keys())
    writer.writeheader()
    writer.writerows(data)
