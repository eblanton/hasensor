import board
import busio
from adafruit_am2320 import AM2320

from ..sensor import ArgDict, Sensor, hexint_parser


class AM2320Sensor(Sensor):
    _argtypes: ArgDict = {
        "address": hexint_parser
    }

    def __init__(self, address: int = 0x5c, **kwargs):
        self.__class__.__base__.type_args(kwargs)
        super().__init__(**kwargs)

        i2c = busio.I2C(board.SCL, board.SDA)
        self._am2320 = AM2320(i2c, address=address)

    def fire(self):
        temp = self._am2320.temperature
        hum = self._am2320.relative_humidity
        self._loop.publish(self.name,
                           '{"temp":%.02f,"humidity":%.02f}' % (temp, hum))
