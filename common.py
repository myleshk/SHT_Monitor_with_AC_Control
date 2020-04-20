import configparser
from firebase import firebase
import time


class Common:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.fb = firebase.FirebaseApplication(
            self.config['Firebase']['db_location'], None)

    def heatIndex(self, T_C, R):
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

        return c1 + c2 * T_F + c3 * R + c4 * T_F * R + c5 * T_F ** 2 + c6 * R ** 2 + c7 * T_F ** 2 * R + c8 * T_F * R ** 2 + c9 * T_F ** 2 * R ** 2

    def reportRecord(self, temperature, humidity, AC_state=None):
        timestamp = int(time.time())

        data = {}
        if AC_state is None:
            data = {timestamp: {"RH": humidity, "T_C": temperature}}
        else:
            data = {timestamp: {"RH": humidity, "T_C": temperature, "AC": AC_state}}

        try:
            self.fb.post('/records', data)
        except Exception as e:
            print(e)
            return False
        return True
