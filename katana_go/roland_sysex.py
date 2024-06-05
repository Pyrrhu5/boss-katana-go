"""Parameters available for sysex message to a Roland device.

References:
    https://cdn.roland.com/assets/media/pdf/TB-3_MI_1.pdf
"""

from importlib.resources import open_text
from dataclasses import dataclass, is_dataclass
from typing import Optional

import yaml

from katana_go import resources


def _nested_dataclass(*args, **kwargs):

    def wrapper(check_class):

        # passing class to investigate
        check_class = dataclass(check_class, **kwargs)
        o_init = check_class.__init__

        def __init__(self, *args, **kwargs):

            for name, value in kwargs.items():

                # getting field type
                ft = check_class.__annotations__.get(name, None)

                if is_dataclass(ft) and isinstance(value, dict):
                    obj = ft(**value)
                    kwargs[name] = obj
                o_init(self, *args, **kwargs)

        check_class.__init__ = __init__

        return check_class

    return wrapper(args[0]) if args else wrapper


@dataclass
class Parameter:
    parameter_id: int
    parameter_sub_id: int


@dataclass
class ParameterValue:
    id: int
    value_1: int
    value_2: int
    max_value: int = 0x2F
    min_value: int = 0x00
    value_3: Optional[int] = None


@_nested_dataclass
class Amp(Parameter):
    """Control the main settings of the amplifier."""
    volume: ParameterValue
    gain: ParameterValue
    bass: ParameterValue
    middle: ParameterValue
    treble: ParameterValue
    presence: ParameterValue


@_nested_dataclass
class ProgramSelect(ParameterValue, Parameter):
    ...


@_nested_dataclass
class RolandSysex:
    amp: Amp
    preset_select: ProgramSelect


roland_sysex: RolandSysex = RolandSysex(
    **yaml.safe_load(open_text(resources, "roland_sysex.yaml"))
)

