import configparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
from heat_index import calculate
from os import path


class Common:
    config_etag = None
    hot_config = None

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
        self.records_db = db.reference('records', app=app)
        self.config_db = db.reference('config', app=app)

    @staticmethod
    def heatIndex(temperature, humidity):
        heat_index = calculate.from_celsius(temperature, humidity)
        return round(heat_index, 2)

    def reportRecord(self, temperature, humidity, HI, AC_state=None):
        timestamp = int(time.time())

        data = {"RH": humidity, "T_C": temperature, "TS": timestamp, "HI": HI}
        if AC_state is not None:
            data["AC"] = AC_state

        try:
            self.records_db.push(data)
        except Exception as e:
            print(e)
            return False
        return True

    def getHotConfig(self):
        try:
            if self.config_etag:
                changed, data, new_etag = self.config_db.get_if_changed(
                    self.config_etag
                )
                if changed:
                    self.config_etag = new_etag
                    self.hot_config = data
            else:
                data, new_etag = self.config_db.get(etag=True)
                self.config_etag = new_etag
                self.hot_config = data

            return self.hot_config
        except Exception as e:
            print(e)
            return None
