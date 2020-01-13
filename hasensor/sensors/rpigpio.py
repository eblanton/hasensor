from typing import Optional

import RPi.GPIO as GPIO

from ..sensor import ArgDict, Sensor


class RPiGPIOSensor(Sensor):
    _argtypes: ArgDict = {
        'pin': int,
        'debounce': int,
        'inverted': bool,
        'power': int
    }

    def __init__(self, pin: Optional[int] = 4, debounce: Optional[int] = 0,
                 inverted: Optional[bool] = False, power: Optional[int] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self._pin = pin
        self._debounce = debounce
        self._power = power
        self._inverted = inverted

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

        if power is not None:
            GPIO.setup(self._power, GPIO.OUT)
            GPIO.output(self._power, GPIO.HIGH)

        if self._debounce:
            GPIO.add_event_detect(self._pin, GPIO.BOTH,
                                  bouncetime=self._debounce,
                                  callback=lambda p: self._detect(p))
        else:
            GPIO.add_event_detect(self._pin, GPIO.BOTH,
                                  callback=lambda p: self._detect(p))

    # This sensor does nothing on fire
    def fire(self):
        pass

    def _state(self, state):
        print(state)
        if (state and not self._inverted) or (not state and self._inverted):
            return "ON"
        return "OFF"

    def _detect(self, pin):
        del pin
        state = self._state(GPIO.input(self._pin))
        self._loop.publish(self.name, state)
