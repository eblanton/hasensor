"""Main loop for a sensor node.

This file provides a mainloop for integrating the sensor node logic
with the paho MQTT loop.  It allows time-scheduled events to be added
to the system and loops only until the next scheduled event occurs.

It does not currently handle reconnection logic, but it should.
"""

import time
from typing import List, TYPE_CHECKING
from heapq import heappush, heappop

import paho.mqtt.client as MQTTClient

from .configuration import Configuration

if TYPE_CHECKING:
    from .event import Event


def _on_connect_cb(client, data, flags, result):
    data._on_connect_cb(client, flags, result)

def _on_disconnect_cb(client, data, result):
    data._on_disconnect_cb(client, result)

class Loop:
    """The main event loop.

    Events can be added to the loop, and their execution will begin as soon as
    a connection with the MQTT broker is established.   Scheduling is on a
    fractional-second basis, but only minimal effort is made to maintain
    timings.  Critical timings (such as I/O interactions) should not rely on
    the loop's scheduler.
    """

    def __init__(self, conf: Configuration):
        """Create a mainloop for sensing.

        The conf parameter provides a required configuration.
        """

        self._conf: Configuration = conf

        # Create the MQTT client
        self._mqttclient = MQTTClient.Client(conf.client_id, userdata=self)
        self._mqttclient.on_connect = _on_connect_cb
        self._mqttclient.on_disconnect = _on_disconnect_cb

        self.prefix = self._conf.prefix

        self._events: List['Event'] = []
        self._mqttclient.connect(self._conf.broker[0], self._conf.broker[1])

        self.connected: bool = False
        """Whether the loop believes it is connected to the server or not.

        This value should only be queried, not set, by external users.
        """

    def _on_connect_cb(self, client: MQTTClient.Client, flags,
                       result: int) -> None:
        if result == 0:
            self.connected = True
        else:
            raise Exception("connection error")

    def _on_disconnect_cb(self, client: MQTTClient.Client, result):
        self.connected = False
        self._mqttclient.reconnect()

    def schedule(self, event: 'Event'):
        """Add an event to the loop's schedule."""
        heappush(self._events, event)

    def publish(self, subtopic, data):
        """Publish a message to the loop's MQTT broker under this sensor's topic."""
        topic = self._conf.prefix + "/" + subtopic
        self._mqttclient.publish(topic, data)

    def publish_raw(self, topic, data):
        """Publish a message to the loop's MQTT broker on any topic."""
        self._mqttclient.publish(topic, data)

    def _process(self, event: 'Event'):
        event.fire()
        if event.repeats:
            self.schedule(event)

    def loop(self):
        """Loop forever, running the scheduled events."""
        if not self._events:
            return

        # Using a heap for the handful of events with multi-second
        # delays between is almost certainly overkill.
        nevent = heappop(self._events)
        while True:
            if not self.connected:
                self._mqttclient.loop(timeout=0.5, max_packets=1)
                continue

            now = time.time()

            # Process all events that happened up to and including now
            while nevent.next_fire <= now:
                self._process(nevent)
                if self._events:
                    nevent = heappop(self._events)
                else:
                    nevent = None
                    break
            if nevent is None:
                break

            # Calculate the difference between now and the next event
            stime = nevent.next_fire - now
            self._mqttclient.loop(timeout=stime)
