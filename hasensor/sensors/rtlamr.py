import json

from subprocess import Popen, DEVNULL, PIPE
from threading import Thread
from typing import Optional

from ..sensor import Sensor, ArgDict


class RTLAMRSensor(Sensor):
    _argtypes: ArgDict = {
        "meter_id": int,
        "symbol_length": int
    }

    _rtl: Popen
    _thread: Thread

    def __init__(self, meter_id: Optional[int] = 0,
                 symbol_length: Optional[int] = 0,
                 **kwargs):
        super().__init__(**kwargs)

        rtlargs = ["rtlamr", "-unique", "-format", "json"]
        if meter_id:
            rtlargs.append("-filterid")
            rtlargs.append(str(meter_id))
        if symbol_length:
            rtlargs.append("-symbollength")
            rtlargs.append(str(symbol_length))

        self._rtl = Popen(rtlargs, stdin=DEVNULL, stdout=PIPE, stderr=DEVNULL,
                          close_fds=True)
        self._thread = Thread(target=self._handle_rtl)
        self._thread.start()

    def fire(self):
        pass

    def _handle_rtl(self):
        while True:
            try:
                packet = self._rtl.stdout.readline()
                if not packet:
                    continue
                info = json.loads(packet)
            except OSError:
                self._rtl.kill()
                return
            if 'Message' in info:
                message = info['Message']
                if 'ID' in message and 'Consumption' in message:
                    self._loop.publish(self.name, '{"id":%d,"kWh":%d}'
                                       % (message['ID'],
                                          message['Consumption']))
