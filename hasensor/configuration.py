"""Configuration for a sensor node.

This file encapsulates the configuration state needed for an entire sensor
node, from the information required to connect to the MQTT broker to the topic
prefix used by the node to the description of its sensors.
"""

import argparse
import socket

from typing import Tuple, List


def _parse_broker(broker: str) -> Tuple[str, int]:
    """Parse a host:port string and return its components."""

    errmsg: str = "bad broker; use host:port"
    host, *port_list = broker.split(':')

    if not host:
        raise Exception(errmsg)

    if not port_list:
        return (host, 1883)

    if len(port_list) == 1:
        port = int(port_list[0])
        if port < 1 or port > 65535:
            raise Exception(errmsg)
        return (host, port)

    raise Exception(errmsg)


class Configuration:
    """Configuration for a sensor node.

    After creating this object, must be filled.  This is typically done by
    calling parse_args with no arguments, filling the configuration in from
    the command line.
    """
    _hostname = socket.gethostname()            # type: str
    DEF_MQTT_CLIENT_ID = ("sensor_%s" % _hostname)  # type: str
    DEF_MQTT_PREFIX = DEF_MQTT_CLIENT_ID        # type: str
    DEF_DISC_PREFIX = "homeassistant"           # type: str
    DEF_DISC_NODE = _hostname                   # type: str
    DEF_DISC_INTERVAL = 60*60                   # type: int

    def __init__(self):
        self.broker: Tuple[str, int] = ("localhost", 1883)
        """The MQTT broker (hostname, port) tuple"""
        self.discoverable: bool = False
        """Whether the sensors on this node should be discoverable by Home Assistant"""
        self.client_id: str = Configuration.DEF_MQTT_CLIENT_ID
        """The client ID used for connecting to the MQTT broker"""
        self.prefix: str = Configuration.DEF_MQTT_PREFIX
        """The MQTT topic prefix used by this sensor node"""
        self.discovery_prefix: str = Configuration.DEF_DISC_PREFIX
        """The discovery topic prefix used for Home Assistant discovery"""
        self.discovery_node: str = Configuration.DEF_DISC_NODE
        """The discovery node ID"""
        self.discovery_interval: int = Configuration.DEF_DISC_INTERVAL
        """The interval at which repeated discovery messages should be sent.

        A value of 0 will send only one discovery message at sensor startup,
        providing that discovery is enabled.
        """
        self.sensors: List[str] = []

    @classmethod
    def _parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Multi-sensor sensor node.")
        parser.add_argument("--broker", "-b", default="localhost",
                            type=_parse_broker,
                            help="MQTT broker (host[:port])")
        parser.add_argument("--client-id", "-c",
                            default=Configuration.DEF_MQTT_CLIENT_ID,
                            type=str, help="MQTT client ID")
        parser.add_argument("--prefix", "-p",
                            default=Configuration.DEF_MQTT_PREFIX,
                            type=str, help="MQTT topic prefix")
        parser.add_argument("--discoverable", "-d", action="store_true",
                            help="Advertise sensors to Home Assistant")
        parser.add_argument("--discovery-prefix", type=str,
                            default=Configuration.DEF_DISC_PREFIX,
                            help="MQTT prefix to use for discovery")
        parser.add_argument("--discovery-interval", type=int,
                            default=Configuration.DEF_DISC_INTERVAL,
                            help="Interval for discovery re-broadcast (seconds; suppress if 0)")
        parser.add_argument("--discovery-node", type=str,
                            default=Configuration.DEF_DISC_NODE,
                            help="Node ID for discovery (omitted if none)")
        parser.add_argument("--sensor", "-s", type=str, action="append",
                            help="Add a sensor description string to the current configuration")
        return parser

    def parse_args(self, filename: str = None) -> None:
        """Parse the command line arguments.

        The contents of the command line arguments will be used to configure
        the event loop, MQTT broker, and sensors.
        """
        parser = Configuration._parser()
        args = None
        if filename is not None:
            raise Exception("File parser not yet implemented")
        else:
            args = parser.parse_args()

        if args.discoverable:
            self.discoverable = args.discoverable
        if args.broker:
            self.broker = args.broker
        if args.client_id:
            self.client_id = args.client_id
        if args.prefix:
            self.prefix = args.prefix
        if args.discovery_prefix:
            self.discovery_prefix = args.discovery_prefix
        if args.discovery_interval:
            self.discovery_interval = args.discovery_interval
        if args.sensor:
            self.sensors = args.sensor
