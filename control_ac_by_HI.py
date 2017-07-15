#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from sht_sensor import Sht
from datetime import datetime
import collections
import requests
from common import Common

cm = Common()
check_interval_sec = int(cm.config['Common']['check_interval_sec'])
history_max_len = int(cm.config['Common']['history_max_len'])
low_HI_thres = float(cm.config['HI']['low_HI_thres'])
high_HI_thres = float(cm.config['HI']['high_HI_thres'])
AC_off_URL = cm.config['Webhook']['AC_off']
AC_on_URL = cm.config['Webhook']['AC_on']

state_on = 0  # 0 for unknown, 1 for on, -1 for off

sht = Sht(cm.config['Hardware']['SCK_BCM_num'], cm.config['Hardware']['DATA_BCM_num'])

history = collections.deque(maxlen=history_max_len)

while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sht.read_rh()
    temperature = sht.read_t()

    if humidity is not None and temperature is not None:
        HI = Common().heatIndex(temperature, humidity)
        history.append(HI)

        # check for action

        if len(history) == history_max_len:

            # we have enough data

            sum = 0

            for one_HI in history:
                sum += one_HI

            average_HI = sum / history_max_len

            # do actions

            if average_HI < low_HI_thres and state_on > -1:

                r = requests.get(AC_off_URL)
                # print 'Turn off A/C'
                state_on = -1

            elif average_HI > high_HI_thres and state_on < 1:

                r = requests.get(AC_on_URL)
                # print 'Turn on A/C'
                state_on = 1

        #report
        cm.reportRecord(temperature, humidity, state_on)
        print '{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}  A/C State={:d}'.format(ts,
                temperature, humidity, HI, state_on)
    else:

        print '{:s}  Failed to get reading. Try again!'.format(ts)

    time.sleep(check_interval_sec)
