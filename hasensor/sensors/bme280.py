from typing import Optional

import board
import busio
import adafruit_bme280

from ..sensor import ArgDict, Sensor, hexint_parser


class BME280Sensor(Sensor):
    _argtypes: ArgDict = {
        "address": hexint_parser
    }

    def __init__(self, address: Optional[int] = 0x77, **kwargs):
        super().__init__(**kwargs)

        i2c = busio.I2C(board.SCL, board.SDA)
        self._bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)

    def fire(self):
        temp = self._bme280.temperature
        humidity = self._bme280.humidity
        pressure = self._bme280.pressure
        self._loop.publish(self.name,
                           '{"temp":%.02f,"humidity":%.02f,"pressure":%.02f}'
                           % (temp, humidity, pressure))
