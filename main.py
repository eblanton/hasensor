#!/usr/bin/python3

import json
from typing import Optional, Tuple

from hasensor.configuration import Configuration
from hasensor.loop import Loop
from hasensor.event import RepeatingEvent, NOW

def send_alive(args: Optional[Tuple[Loop, str]]) -> None:
    print("Sending keepalive")
    if args is None:
        return
    loop, topic = args
    loop.publish(topic, "ON")


def send_discovery(args: Optional[Tuple[Loop, Configuration]]) -> None:
    disc_prefix = conf.discovery_prefix
    prefix = conf.prefix
    if conf.alive_interval != 0:
        alive_prefix = "%s/binary_sensor/%sOnline/config" % (disc_prefix, conf.discovery_node)
        loop.publish(alive_prefix,
                     json.dumps({"state_topic": "%s/state" % prefix,
                                 "name": "%s Online" % conf.discovery_node}))


class DiscoveryEvent(RepeatingEvent):
    def __init__(self, conf: Configuration):
        super().__init__(NOW, conf.discovery_interval, send_discovery, conf)

        # Cheat a little
        if conf.discovery_interval == 0:
            self.repeats = False


if __name__ == "__main__":
    conf = Configuration()
    conf.parse_args()

    loop = Loop(conf)

    if conf.alive_interval > 0:
        loop.schedule(RepeatingEvent(NOW, conf.alive_interval, send_alive,
                                     (loop, conf.prefix + "/state")))
    if conf.discoverable:
        loop.schedule(DiscoveryEvent(conf))

    loop.loop()
