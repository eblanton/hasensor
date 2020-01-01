import json
from typing import Dict, List

import psutil                           # type: ignore

from ..sensor import ArgDict, Sensor


class SystemSensor(Sensor):
    _argtypes: ArgDict = {
        "partitions": str,
        "diskthresh": float
    }

    def __init__(self, partitions: str = "", diskthresh: float = 0.0,
                 **kwargs):
        self.__class__.__base__.type_args(kwargs)       # type: ignore
        super().__init__(**kwargs)

        if partitions:
            self._partitions = partitions.split(',')
        else:
            self._partitions = []

        self._diskthresh = diskthresh

    def fire(self):
        stats: Dict[str, str] = {}

        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read())
        f_temp = float(temp) / 1000.0
        stats["cpu_temp"] = "%0.1f" % f_temp

        stats["cpu_pct"] = "%0.1f" % psutil.cpu_percent()
        stats["mem_used_pct"] = "%0.1f" % psutil.virtual_memory().percent

        if self._diskthresh != 0.0:
            warnings: List[str] = []
            if self._partitions:
                for part in self._partitions:
                    if psutil.disk_usage(part).percent > self._diskthresh:
                        warnings.append(part)
            else:
                for part in psutil.disk_partitions():
                    usage = psutil.disk_usage(part.mountpoint)
                    if usage.percent > self._diskthresh:
                        warnings.append(part.mountpoint)
            if warnings:
                stats["disk_full"] = warnings

        self._loop.publish(self.name, json.dumps(stats))
