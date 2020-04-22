#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime
import collections
import requests
from common import Common
from sensor import Sensor

cm = Common()
check_interval_sec = int(Common.config['Common']['check_interval_sec'])
history_max_len = int(Common.config['Common']['history_max_len'])
low_RH_thres = float(Common.config['RH']['low_RH_thres'])
high_RH_thres = float(Common.config['RH']['high_RH_thres'])
AC_off_URL = Common.config['Webhook']['AC_off']
AC_on_URL = Common.config['Webhook']['AC_on']

state_on = 0  # 0 for unknown, 1 for on, -1 for off

sensor = Sensor()

history = collections.deque(maxlen=history_max_len)

while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sensor.read_rh()
    temperature = sensor.read_t()

    if humidity is not None and temperature is not None:
        HI = Common.heatIndex(temperature, humidity)
        history.append(humidity)

        # check for action

        if len(history) == history_max_len:

            # we have enough data

            sum = 0

            for one_humidity in history:
                sum += one_humidity

            average_RH = sum / history_max_len

            # do actions

            try:
                if average_RH < low_RH_thres and state_on > -1:

                    r = requests.get(AC_off_URL)
                    # 'Turn off A/C'
                    state_on -= 1

                elif average_RH > high_RH_thres and state_on < 1:

                    r = requests.get(AC_on_URL)
                    # 'Turn on A/C'
                    state_on += 1
            except Exception as e:
                print("Failed to control A/C. Error as following:")
                print(e)

        # report
        report_result = "Reported" if cm.reportRecord(
            temperature, humidity, HI, state_on
        ) else "Report Error"

        print('{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}  A/C State={:d}  {:s}'.format(
            ts, temperature, humidity, HI, state_on, report_result))
    else:
        print('{:s}  Failed to get reading. Try again!'.format(ts))

    time.sleep(check_interval_sec)
