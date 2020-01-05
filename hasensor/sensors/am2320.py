from typing import Optional

import board
import busio
from adafruit_am2320 import AM2320

from ..sensor import ArgDict, Sensor, hexint_parser


class AM2320Sensor(Sensor):
    _argtypes: ArgDict = {
        "address": hexint_parser,
        "ewma": bool,
        "alpha": float
    }

    def __init__(self, address: Optional[int] = 0x5c,
                 ewma: Optional[bool] = False, alpha: Optional[float] = 0.7,
                 **kwargs):
        super().__init__(**kwargs)

        i2c = busio.I2C(board.SCL, board.SDA)
        self._am2320 = AM2320(i2c, address=address)
        self._ewma = ewma
        self._alpha = alpha

        self._prev_temp: Optional[float] = None
        self._prev_hum: Optional[float] = None

    def fire(self):
        temp = self._am2320.temperature
        hum = self._am2320.relative_humidity

        if self._ewma and self._prev_temp is not None:
            temp = temp * self._alpha + self._prev_temp * (1 - self._alpha)
            hum = hum * self._alpha + self._prev_hum * (1 - self._alpha)
            self._prev_temp = temp
            self._prev_hum = hum
        elif self._ewma:
            self._prev_temp = temp
            self._prev_hum - hum

        self._loop.publish(self.name,
                           '{"temp":%.02f,"humidity":%.02f}' % (temp, hum))
