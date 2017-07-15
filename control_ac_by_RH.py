#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from sht_sensor import Sht
from datetime import datetime
import configparser
import collections
import requests
from common import Common

config = configparser.ConfigParser()
config.read("config.ini")

check_interval_sec = int(config['Common']['check_interval_sec'])
history_max_len = int(config['Common']['history_max_len'])
low_RH_thres = float(config['RH']['low_RH_thres'])
high_RH_thres = float(config['RH']['high_RH_thres'])
AC_off_URL = config['Webhook']['AC_off']
AC_on_URL = config['Webhook']['AC_on']

state_on = 0  # 0 for unknown, 1 for on, -1 for off

sht = Sht(config['Hardware']['SCK_BCM_num'], config['Hardware']['DATA_BCM_num'])

history = collections.deque(maxlen=history_max_len)

while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sht.read_rh()
    temperature = sht.read_t()

    if humidity is not None and temperature is not None:
        HI = Common().heatIndex(temperature, humidity)
        history.append(humidity)

        # check for action

        if len(history) == history_max_len:

            # we have enough data

            sum = 0

            for one_humidity in history:
                sum += one_humidity

            average_RH = sum / history_max_len

            # do actions

            if average_RH < low_RH_thres and state_on > -2:

                r = requests.get(AC_off_URL)
                # print 'Turn off A/C'
                state_on -= 1

            elif average_RH > high_RH_thres and state_on < 2:

                r = requests.get(AC_on_URL)
                # print 'Turn on A/C'
                state_on += 1

        print '{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}  A/C State={:d}'.format(ts,
                temperature, humidity, HI, state_on)
    else:

        print '{:s}  Failed to get reading. Try again!'.format(ts)

    time.sleep(check_interval_sec)
