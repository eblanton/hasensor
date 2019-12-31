from typing import Dict, Optional, TypeVar, Type

from .sensor import Sensor

SensorType = TypeVar('SensorType', bound=Sensor)
"""Any type derived from Sensor."""

# For some reason I cannot make this type checking work.
_sensor_registry = {}                   # type: ignore


def register_sensor_type(name: str, sensor: Type[SensorType]) -> None:
    """Register a sensor type for later creation.

    The name is the name of the sensor as you would describe it in a
    configuration.  The same sensor can be registered under more than
    one name, but it cannot tell under which name it was instantiated.
    """
    if name in _sensor_registry:
        raise Exception("duplicate sensor definition")
    _sensor_registry[name] = sensor


def create_sensor(desc: str) -> SensorType:
    """Create a sensor from a description string.

    The description string is of the form:
      "name:bool_arg:arg=value"

    The sensor registered as type "name" will be looked up, and its class
    used to construct the object.  The arguments will be split on the colons,
    and separated into key=value pairs.  Keys without values will be passed
    on with a None value, which will assumed to be a boolean that is True if
    type allows.
    """
    name, *args = desc.split(':')

    kwargs: Dict[str, Optional[str]] = {}
    for arg in args:
        key, *val = arg.split('=', 1)
        if val:
            kwargs[key] = val[0]
        else:
            kwargs[key] = None

    if name not in _sensor_registry:
        raise Exception("unknown sensor %s" % name)

    sensorcls = _sensor_registry[name]
    sensorcls.type_args(kwargs)

    return _sensor_registry[name](**kwargs)
