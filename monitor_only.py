#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime
from common import Common
from sensor import Sensor

cm = Common()
check_interval_sec = int(Common.config['Common']['check_interval_sec'])

sensor = Sensor()

while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sensor.read_rh()
    temperature = sensor.read_t()

    if humidity is not None and temperature is not None:
        HI = Common.heatIndex(temperature, humidity)
        # report
        cm.reportRecord(temperature, humidity)
        print('{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}'.format(
            ts, temperature, humidity, HI
        ))
    else:
        print('{:s} Failed to get reading. Try again!'.format(ts))

    time.sleep(check_interval_sec)
