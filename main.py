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
low_HI_thres = float(Common.config['HI']['low_HI_thres'])
high_HI_thres = float(Common.config['HI']['high_HI_thres'])
low_RH_thres = float(Common.config['RH']['low_RH_thres'])
high_RH_thres = float(Common.config['RH']['high_RH_thres'])
AC_off_URL = Common.config['Webhook']['AC_off']
AC_on_URL = Common.config['Webhook']['AC_on']

state_on = 0  # 0 for unknown, 1 for on, -1 for off

sensor = Sensor()
history = collections.deque(maxlen=history_max_len)


def turn_off_AC:
    try:
        r = requests.get(AC_off_URL)
        state_on = -1
    except Exception as e:
        print("Failed to control A/C. Error as following:")
        print(e)


def turn_on_AC:
    try:
        r = requests.get(AC_on_URL)
        state_on = 1
    except Exception as e:
        print("Failed to control A/C. Error as following:")
        print(e)


while True:

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity = sensor.read_rh()
    temperature = sensor.read_t()

    if humidity is not None and temperature is not None:
        HI = Common.heatIndex(temperature, humidity)

        control_factor = None
        low_factor_thres = None
        high_factor_thres = None

        # get control_type
        control_type = cm.getHotConfig()['control_type']

        if control_type == 'HI':
            control_factor = HI
            low_factor_thres = low_HI_thres
            high_factor_thres = high_HI_thres
        elif control_type == 'RH':
            control_factor = humidity
            low_factor_thres = low_RH_thres
            high_factor_thres = high_RH_thres

        if control_factor and low_factor_thres and high_factor_thres:
            history.append(control_factor)
            # check for action
            if len(history) == history_max_len:
                # we have enough data
                control_factor_sum = 0
                for control_factor_in_history in history:
                    control_factor_sum += control_factor_in_history
                average_control_factor = control_factor_sum / history_max_len

                # do actions
                if average_control_factor < low_factor_thres and state_on > -1:
                    turn_off_AC()
                elif average_control_factor > high_factor_thres and state_on < 1:
                    turn_on_AC()

        # report
        cm.reportRecord(temperature, humidity, HI, state_on)
        print('{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}  A/C State={:d} Control type "{:s}"'.format(
            ts, temperature, humidity, HI, state_on, control_type
        ))
    else:
        print('{:s}  Failed to get reading. Try again!'.format(ts))

    time.sleep(check_interval_sec)