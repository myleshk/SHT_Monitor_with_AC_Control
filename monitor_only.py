#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import configparser
from sht_sensor import Sht
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")

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


while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sht.read_rh()
    temperature = sht.read_t()

    if humidity is not None and temperature is not None:
        HI = heatIndex(temperature, humidity)

        print '{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}'.format(ts,
                temperature, humidity, HI)
    else:

        print '{:s} Failed to get reading. Try again!'.format(ts)

    time.sleep(int(config['Common']['check_interval_sec']))

