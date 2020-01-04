from ..sensor import ArgDict, Sensor


class Announcer(Sensor):
    _argtypes: ArgDict = {
        "value": str
    }

    def __init__(self, value: str = "ON", **kwargs):
        self.__class__.__base__.type_args(kwargs)       # type: ignore
        super().__init__(**kwargs)

        self._value = value

    def fire(self):
        self._loop.publish(self.name, self._value)
