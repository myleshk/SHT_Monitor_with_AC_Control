#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from sht_sensor import Sht
from datetime import datetime
import configparser
import collections
import requests

config = configparser.ConfigParser()
config.read("config.ini")

history_max_len = int(config['Common']['history_max_len'])
low_HI_thres = float(config['HI']['low_HI_thres'])
high_HI_thres = float(config['HI']['high_HI_thres'])
AC_off_URL = config['Webhook']['AC_off']
AC_on_URL = config['Webhook']['AC_on']

state_on = 0  # 0 for unknown, 1 for on, -1 for off

sht = Sht(config['Hardware']['SCK_BCM_num'], config['Hardware']['DATA_BCM_num'])

def heatIndex(T_C, R):
    T_F = T_C * 1.8 + 32

    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783e-3
    c6 = -5.481717e-2
    c7 = 1.22874e-3
    c8 = 8.5282e-4
    c9 = -1.99e-6

    return c1 + c2 * T_F + c3 * R + c4 * T_F * R + c5 * T_F ** 2 + c6 \
        * R ** 2 + c7 * T_F ** 2 * R + c8 * T_F * R ** 2 + c9 * T_F \
        ** 2 * R ** 2

history = collections.deque(maxlen=history_max_len)

while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sht.read_rh()
    temperature = sht.read_t()

    if humidity is not None and temperature is not None:
        HI = heatIndex(temperature, humidity)
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

        print '{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}  A/C State={:d}'.format(ts,
                temperature, humidity, HI, state_on)
    else:

        print '{:s}  Failed to get reading. Try again!'.format(ts)

    time.sleep(int(config['Common']['check_interval_sec']))

