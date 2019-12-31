"""Sensor node events."""

import time
from functools import total_ordering
from typing import Any, Callable, Optional

from .loop import Loop

EventCallback = Callable[[Optional[Any]], None]
"""The type for callbacks passed to the Event constructor."""

NOW = 0                 # type: int
""" The time Now can be used to schedule an event as soon as possible."""


@total_ordering
class Event:
    """Event is the base class for all loop events in this package.

    An instantiation of Event represents an event that fires once, calling its
    callback at the scheduled time.
    """

    def __init__(self, t: float, callback: EventCallback = None,
                 data: Any = None):
        """Creates an event that fires at time t.

        The callback will be called with data as an argument
        at time t.
        """
        self.repeats: bool = False
        self.next_fire: float = t
        self.callback: Optional[EventCallback] = callback
        self.data: Any = data

        if t == NOW:
            self.next_fire = time.time()

    def __eq__(self, other):
        return self.next_fire == other.next_fire

    def __ne__(self, other):
        return self.next_fire != other.next_fire

    def __lt__(self, other):
        return self.next_fire < other.next_fire

    def fire(self) -> None:
        """Execute this event's callback with its given data."""
        if self.callback is not None:
            self.callback(self.data)

    def reschedule(self, loop: Loop) -> None:
        """Reschedule this event on the given loop (no-op)."""


class RepeatingEvent(Event):
    """An event that repeats on a fixed period.

    This event will not reschedule itself, but the loop will automatically
    reschedule it.
    """

    def __init__(self, t: float, period: float,
                 callback: EventCallback = None, data: Any = None):
        """Creates a repeating event.

        The event will first fire at time t, then every period
        seconds thereafter.
        """
        super().__init__(t, callback, data)

        self.repeats = True
        self.period = period

    def fire(self) -> None:
        """Execute this event's callback with its given data, and update its
        next firing time.
        """
        super().fire()
        self.next_fire += self.period

    def reschedule(self, loop):
        """Reschedule this event on the given loop."""
        loop.schedule(self, self.next_fire)
