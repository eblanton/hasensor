#!/usr/bin/python3

from typing import Optional, Tuple

from hasensor.configuration import Configuration
from hasensor.loop import Loop
from hasensor.event import RepeatingEvent, NOW
from hasensor.sensor import Sensor

from hasensor.registry import register_sensor_type, create_sensor
from hasensor.sensors.system import SystemSensor
from hasensor.sensors.announcer import Announcer
try:
    from hasensor.sensors.bme280 import BME280Sensor
    from hasensor.sensors.am2320 import AM2320Sensor
    _have_board = True
except NotImplementedError:
    _have_board = False


def send_discovery(args: Optional[Tuple[Loop, Configuration]]) -> None:
    disc_prefix = conf.discovery_prefix
    prefix = conf.prefix
    if conf.alive_interval != 0:
        alive_prefix = "%s/binary_sensor/%sOnline/config" % (disc_prefix, conf.discovery_node)
        loop.publish_raw(alive_prefix, '{"state_topic":"%s/state","name":"%s Online"}' %
                         (prefix, conf.discovery_node))


class DiscoveryEvent(RepeatingEvent):
    def __init__(self, conf: Configuration):
        super().__init__(NOW, conf.discovery_interval, send_discovery, conf)

        # Cheat a little
        if conf.discovery_interval == 0:
            self.repeats = False


if __name__ == "__main__":
    register_sensor_type("system", SystemSensor)
    register_sensor_type("announcer", Announcer)
    if _have_board:
        register_sensor_type("bme280", BME280Sensor)
        register_sensor_type("am2320", AM2320Sensor)

    conf = Configuration()
    conf.parse_args()

    loop = Loop(conf)

    if conf.discoverable:
        loop.schedule(DiscoveryEvent(conf))

    for desc in conf.sensors:
        s: Sensor = create_sensor(desc)
        s.set_loop(loop)
        loop.schedule(s.event())

    loop.loop()
