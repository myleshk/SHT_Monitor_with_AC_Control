#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import configparser
from sht_sensor import Sht
from datetime import datetime
from common import Common

config = configparser.ConfigParser()
config.read("config.ini")

check_interval_sec = int(config['Common']['check_interval_sec'])

sht = Sht(config['Hardware']['SCK_BCM_num'],
          config['Hardware']['DATA_BCM_num'])


while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sht.read_rh()
    temperature = sht.read_t()

    if humidity is not None and temperature is not None:
        HI = Common.heatIndex(temperature, humidity)

        print '{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}'.format(ts, temperature, humidity, HI)
    else:

        print '{:s} Failed to get reading. Try again!'.format(ts)

    time.sleep(check_interval_sec)
