#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from sht_sensor import Sht
from datetime import datetime
from common import Common

cm = Common()
check_interval_sec = int(cm.config['Common']['check_interval_sec'])

sht = Sht(cm.config['Hardware']['SCK_BCM_num'],
          cm.config['Hardware']['DATA_BCM_num'])


while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sht.read_rh()
    temperature = sht.read_t()

    if humidity is not None and temperature is not None:
        HI = Common().heatIndex(temperature, humidity)
        # report
        cm.reportRecord(temperature, humidity)
        print('{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}'.format(
            ts, temperature, humidity, HI
        ))
    else:

        print('{:s} Failed to get reading. Try again!'.format(ts))

    time.sleep(check_interval_sec)
