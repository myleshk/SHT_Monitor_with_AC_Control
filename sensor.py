from common import Common
from sht_sensor import Sht
from adafruit_dht import DHT11


class ChipModelException(Exception):
    def __init__(self):
        pass


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
        else:
            raise ChipModelException

    def read_rh(self):
        if self.chip_model == 'SHT-75':
            return self.chip.read_rh()
        elif self.chip_model == 'DHT-11':
            try:
                return self.chip.humidity
            except RuntimeError:
                return None
        else:
            raise ChipModelException

    def read_t(self):
        if self.chip_model == 'SHT-75':
            return self.chip.read_t()
        elif self.chip_model == 'DHT-11':
            try:
                return self.chip.temperature
            except RuntimeError:
                return None
        else:
            raise ChipModelException
