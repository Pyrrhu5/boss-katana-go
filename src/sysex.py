"""Within the SYSEX protocol, list of parameters available reserved by the MIDI protocol.

References:
    https://drive.google.com/file/d/1EvdEZf_XqmkoeUmrFhfIM2ZX_Su-4cm-/view
"""

from enum import Enum


class NonRealTime(Enum):
    vendor_id = 0x7E
    general_information = Enum("GeneralInformation", {"identity_request": 0x01})


class RealTime(int, Enum):
    vendor_id = 0x7F
