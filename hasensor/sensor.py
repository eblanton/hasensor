"""The Sensor base class and associated helpers.

New sensors should derive from Sensor, and may wish to use some of the
helper functions provided here.
"""
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .event import Event, RepeatingEvent, NOW
from .loop import Loop

ArgDict = Dict[str, Union[Type, Callable[[str], Any]]]


def _sensor_callback(sensor: Optional['Sensor']) -> None:
    if sensor is not None:
        sensor.fire()


def hexint_parser(arg: str) -> int:
    """Parse a hexadecimal starting with 0x into an integer."""
    if not arg.startswith("0x"):
        raise Exception("Received non-hex integer where hex expected")
    return int(arg, 16)


def time_parser(arg: str) -> float:
    """Parse a start time as either NOW or a float into a float."""
    if arg == "NOW":
        return NOW
    return float(arg)


def type_args(cls: Type['Sensor'], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dict of typed arguments for a sensor.

    Sensors are typically created from a description string, which has
    only string arguments.  This method walks the class hierarchy for a given
    Sensor type and types the arguments for each level.

    This function should be called on the arguments split out of a description
    string before passing it to a sensor.
    """
    args = kwargs
    typed: Dict[str, Any] = {}
    while cls is not object:
        done: List[str] = []
        for arg, value in args.items():
            if arg in cls._argtypes:
                done.append(arg)
                if value is not None:
                    typed[arg] = cls._argtypes[arg](value)
                elif cls._argtypes[arg] is bool:
                    typed[arg] = True
                else:
                    raise Exception("missing argument where required")
        for arg in done:
            del args[arg]
        cls = cls.__base__

    if args:
        # Python uses TypeError for unrecognized keyword arguments
        raise TypeError("Unexpected keyword arguments: %s" % (", ".join(args)))

    return typed


class Sensor:
    """Base class for all sensor objects.

    This provides the basic functionality of a do-nothing sensor; it can
    be scheduled, but when it fires it does nothing but print a diagnostic.
    """

    _argtypes: ArgDict = {
        'name': str,
        'start': time_parser,
        'period': float
    }

    def __init__(self, name: Optional[str] = "Sensor",
                 start: float = NOW, period: float = 0.0):
        """Initialize a new Sensor with a schedule.

        keyword arguments:
          - name:   The name of this sensor (typically used as its MQTT
                    subtopic, but this base class does not use it)
          - start:  The time of the first firing of this sensor's event
          - period: The period of this sensor's event
        """
        self.name = name
        self.start = start
        self.period = period
        self._event: Optional[Event] = None
        self._loop: Optional[Loop] = None

    def set_loop(self, loop: Loop) -> None:
        """Set the event loop that this sensor will be scheduled on."""
        self._loop = loop

    def event(self) -> Event:
        """Create or retrieve an event that will fire this sensor."""
        if self._event is not None:
            return self._event
        if self._loop is None:
            raise Exception("Cannot retrieve sensor event without a loop")

        if self.period == 0.0:
            self._event = Event(self.start, _sensor_callback, self)
        else:
            self._event = RepeatingEvent(self.start, self.period,
                                         _sensor_callback, self)
        return self._event

    def fire(self) -> None:
        """The method called by this sensor's event, to be overridden."""
        print("Firing base Sensor event")
