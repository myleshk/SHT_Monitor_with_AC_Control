from common import Common
from sht_sensor import Sht
from adafruit_dht import DHT11
from time import time
import serial
import re


class ChipModelException(Exception):
    def __init__(self):
        pass


class ArduinoAsChip:
    rh = None
    t = None
    last_read = 0

    def __init__(self):
        self.serial = serial.Serial(Common.config['Hardware']['serial_path'])

    def _read_from_serial(self):
        regex = r"^h:(?P<hum>[\d.]+),t:(?P<temp>[\d.]+)$"
        if time() - self.last_read >= 1 and self.serial.in_waiting > 0:
            dataLine = self.serial.readline()
            matched = re.match(regex, dataLine)
            if matched:
                self.rh = float(matched.group('hum'))
                self.t = float(matched.group('temp'))
                self.last_read = time()
            else:
                # reading error
                pass

    def read_rh(self):
        self._read_from_serial()
        return self.rh

    def read_t(self):
        self._read_from_serial()
        return self.t

    def close(self):
        ser.close()


class Sensor:
    def __init__(self):
        self.chip_model = Common.config['Hardware']['chip_model']
        if self.chip_model == 'SHT-75':
            self.chip = Sht(
                Common.config['Hardware']['SCK_BCM_num'], Common.config['Hardware']['DATA_BCM_num']
            )
        elif self.chip_model == 'DHT-11':
            self.chip = DHT11(
                Common.config['Hardware']['DATA_BCM_num']
            )
        elif self.chip_model == 'Arduino':
            self.chip = ArduinoAsChip()
        else:
            raise ChipModelException

    def read_rh(self):
        if self.chip_model == 'SHT-75' or self.chip_model == 'Arduino':
            return self.chip.read_rh()
        elif self.chip_model == 'DHT-11':
            try:
                return self.chip.humidity
            except RuntimeError:
                return None
            return self.chip.read_rh()
        else:
            raise ChipModelException

    def read_t(self):
        if self.chip_model == 'SHT-75' or self.chip_model == 'Arduino':
            return self.chip.read_t()
        elif self.chip_model == 'DHT-11':
            try:
                return self.chip.temperature
            except RuntimeError:
                return None
        else:
            raise ChipModelException
