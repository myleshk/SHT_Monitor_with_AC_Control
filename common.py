import configparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
from heat_index import calculate
from os import path


class Common:
    def __init__(self):
        Common.config = configparser.ConfigParser()
        Common.config.read("config.ini")
        cred = credentials.Certificate(
            path.join(path.dirname(__file__), 'serviceAccountKey.json')
        )
        app = firebase_admin.initialize_app(
            credential=cred,
            options={
                'databaseURL': Common.config['Firebase']['db_location']
            },
            name=Common.config['Firebase']['project_name']
        )
        self.db = db.reference('records', app=app)

    @staticmethod
    def heatIndex(temperature, humidity):
        heat_index = calculate.from_celsius(temperature, humidity)
        return round(heat_index, 2)

    def reportRecord(self, temperature, humidity, AC_state=None):
        timestamp = int(time.time())

        data = {"RH": humidity, "T_C": temperature, "TS": timestamp}
        if AC_state is not None:
            data["AC"] = AC_state

        try:
            self.db.push(data)
        except Exception as e:
            print(e)
            return False
        return True
