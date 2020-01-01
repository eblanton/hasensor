"""The Sensor base class and associated helpers.

New sensors should derive from Sensor, and may wish to use some of the
helper functions provided here.
"""
from typing import Any, Callable, Dict, Optional, TypeVar, Type, Union

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

    def __init__(self, name: str = "Sensor", start: float = NOW,
                 period: float = 0.0):
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

    def set_loop(self, loop: Loop):
        """Set the event loop that this sensor will be scheduled on."""
        self._loop = loop

    def event(self):
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

    def fire(self):
        """The method called by this sensor's event, to be overridden."""
        print("Firing base Sensor event")

    @classmethod
    def type_args(cls, args: Dict[str, Optional[Any]]):
        """Give the arguments to this sensor a type.

        Sensors are typically created from a description string, which has
        only string arguments.  This method allows each level of the sensor
        class hierarchy to define its arguments with a type, parse the string
        arguments into their types, and then pass the typed arguments to
        super().__init__().

        Subclasses of Sensor should call something like
        self.__class__.__base__.type_args(kwargs) on the keyword arguments
        they do not recognize, then pass the result to super().__init__().
        This will leave any arguments unrecognized by the parent class as
        strings to be recursively typed by that initializer.  The type_args()
        function for Sensor itself will throw an exception on arguments it does
        not recognize.
        """
        for k in args.keys():
            if k in cls._argtypes:
                v = args[k]             # Required to appease the type checker
                if v is not None:
                    args[k] = cls._argtypes[k](v)
                elif cls._argtypes[k] is bool:
                    args[k] = False
                else:
                    raise Exception("Missing argument where required")

            elif cls.__class__ is Sensor:
                # Python uses TypeError for unrecognized keyword arguments
                raise TypeError("Unexpected keyword argument '%s'" % k)
