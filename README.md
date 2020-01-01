Home Assistant/Automation Sensors
===

This package provides a HA sensor service for Raspberry Pi computers
communicating via MQTT.  It is designed to integrate easily with [Home
Assistant](https://home-assistant.io/), although it could be used with
any service.

Using the Demonstration Script
---

The `main.py` here is currently more of a demonstration than a
complete project, but ... that said, I'm using it.  It has a number of
arguments that should be straightforward if you're familiar with MQTT
and Home Assistant (although not all are complete, like
discoverability, which requires more implementation in the individual
sensors), but the sensor configuration is unique to this package.

The `-s` (or `--sensor`) argument accepts a _sensor description_,
which is a string that includes the type of the sensor plus whatever
arguments and configuration it may require/accept.  It is a set of
options separated by colons, like:

```
bme280:name=climate:start=NOW:period=300:address=0x76
```

This declares that you want a BME280 sensor, that it is a periodic
sensor that should start as soon as possible and fire once every 300
seconds, that its MQTT subtopic (which is appended to the prefix
supplied with `-p`) is `climate`, and that it should be found at the
I2C address 0x76 instead of the default 0x77.

Every sensor supports a few arguments:

 * `name`: This is the MQTT subtopic for this sensor.  This will be
   appended to the package topic provided with `-p` on the command
   line to create the topic on which the sensor readings will be
   reported.  For example, if you run with `-p bedroom/master` and
   `name=climate`, you'll get readings on the topic
   `bedroom/master/climate`.
 * `start`: This is the time (in floating point seconds since the
   Epoch) at which the first sensor reading should be taken and
   reported.  The special value `NOW` means to start as soon as the
   sensor is created.
 * `period`: This is a relative number of floating point seconds
   between sensor readings.  If `period` is not supplied, or is
   supplied as 0, the sensor will fire only once.

Other arguments, such as the `address` of the BME280, are
sensor-specific.  Every sensor-derived class should have an
`_argtypes` class variable declaring the arguments it accepts and
their types, if no other documentation is forthcoming.
