#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime
import collections
import requests
from common import Common
from sensor import Sensor
from timeBasedThreshold import Threshold

cm = Common()
check_interval_sec = int(Common.config['Common']['check_interval_sec'])
history_max_len = int(Common.config['Common']['history_max_len'])
AC_off_URL_1 = Common.config['Webhook']['AC_off_1']
AC_on_URL_1 = Common.config['Webhook']['AC_on_1']
AC_off_URL_2 = Common.config['Webhook']['AC_off_2']
AC_on_URL_2 = Common.config['Webhook']['AC_on_2']
th = Threshold(common=cm)

state_on = 0  # 0 for unknown, 1 for on, -1 for off

sensor = Sensor()
history = collections.deque(maxlen=history_max_len)


def toggle_AC(on, item1=False, item2=False):
    global state_on
    webhook_URL_1 = AC_on_URL_1 if on else AC_off_URL_1
    webhook_URL_2 = AC_on_URL_2 if on else AC_off_URL_2
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    state_on = 1 if on else -1
    try:
        if item1:
            r1 = requests.get(webhook_URL_1)
            print(f"{ts} #1 - state: {state_on}. {r1.text}")
        if item2:
            r2 = requests.get(webhook_URL_2)
            print(f"{ts} #2 - state: {state_on}. {r2.text}")
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

        # get hot configs
        control_type = cm.getHotConfig()['control_type']
        low_RH_thres = float(cm.getHotConfig()['low_RH_thres'])
        high_RH_thres = float(cm.getHotConfig()['high_RH_thres'])
        item1_controlled = bool(cm.getHotConfig()['item1_controlled'])
        item2_controlled = bool(cm.getHotConfig()['item2_controlled'])

        # get hot configs from th
        low_HI_thres = th.low_HI_thres()
        high_HI_thres = th.high_HI_thres()

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
                    toggle_AC(False, item1_controlled, item2_controlled)
                elif average_control_factor > high_factor_thres and state_on < 1:
                    toggle_AC(True, item1_controlled, item2_controlled)

        # report
        cm.reportRecord(temperature, humidity, HI, state_on)
        print('{:s}  Temp={:.2f}*C  RH={:.2f}%  HI={:.2f}  A/C State={:d} Control type "{:s}"'.format(
            ts, temperature, humidity, HI, state_on, control_type
        ))
    else:
        print('{:s}  Failed to get reading. Try again!'.format(ts))

    time.sleep(check_interval_sec)
