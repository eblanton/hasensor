#!/usr/bin/python3
"""Generic sensor script."""

from typing import Optional, Tuple

from hasensor.configuration import Configuration
from hasensor.loop import Loop
from hasensor.event import RepeatingEvent, NOW
from hasensor.sensor import Sensor

from hasensor.registry import register_sensor_type, create_sensor
from hasensor.sensors.system import SystemSensor
from hasensor.sensors.announcer import Announcer
from hasensor.sensors.rtlamr import RTLAMRSensor
try:
    from hasensor.sensors.bme280 import BME280Sensor
    from hasensor.sensors.am2320 import AM2320Sensor
    _HAVE_BOARD = True
except NotImplementedError:
    _HAVE_BOARD = False

try:
    from hasensor.sensors.rpigpio import RPiGPIOSensor
    _HAVE_PI = True
except ModuleNotFoundError:
    _HAVE_PI = False


def _send_discovery(args: Optional[Tuple[Loop, Configuration]]) -> None:
    if args is None:
        return
    loop, conf = args
    disc_prefix = conf.discovery_prefix
    prefix = conf.prefix
    if conf.discovery_interval != 0:
        alive_prefix = "%s/binary_sensor/%sOnline/config" \
            % (disc_prefix, conf.discovery_node)
        loop.publish_raw(alive_prefix,
                         '{"state_topic":"%s/state","name":"%s Online"}'
                         % (prefix, conf.discovery_node))


class _DiscoveryEvent(RepeatingEvent):
    def __init__(self, conf: Configuration):
        super().__init__(NOW, conf.discovery_interval, _send_discovery, conf)

        # Cheat a little
        if conf.discovery_interval == 0:
            self.repeats = False


def _main():
    register_sensor_type("system", SystemSensor)
    register_sensor_type("announcer", Announcer)
    register_sensor_type("rtlamr", RTLAMRSensor)
    if _HAVE_BOARD:
        register_sensor_type("bme280", BME280Sensor)
        register_sensor_type("am2320", AM2320Sensor)
    if _HAVE_PI:
        register_sensor_type("gpio", RPiGPIOSensor)

    conf = Configuration()
    conf.parse_args()

    loop = Loop(conf)

    if conf.discoverable:
        loop.schedule(_DiscoveryEvent(conf))

    for desc in conf.sensors:
        sensor: Sensor = create_sensor(desc)
        sensor.set_loop(loop)
        loop.schedule(sensor.event())

    loop.loop()


if __name__ == "__main__":
    _main()
