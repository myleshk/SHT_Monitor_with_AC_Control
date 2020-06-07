from common import Common
from datetime import datetime, time


class Threshold:
    def __init__(self):
        self.cm = Common()

    def _is_daytime(self):
        current_time = datetime.now().time()
        return current_time > time(8, 10) and current_time < time(23, 30):

    def high_HI_thres(self):
        return self._daytime_high_HI_thres() if self._is_daytime else self._night_high_HI_thres()

    def low_HI_thres(self):
        return self._daytime_low_HI_thres() if self._is_daytime else self._night_low_HI_thres()

    def _night_shift_amount(self):
        return float(self.cm.getHotConfig()['HI_night_shift'])

    def _daytime_high_HI_thres(self):
        return float(self.cm.getHotConfig()['high_HI_thres'])

    def _night_high_HI_thres(self):
        return self._daytime_high_HI_thres() + self._night_shift_amount

    def _daytime_low_HI_thres(self):
        return float(self.cm.getHotConfig()['low_HI_thres'])

    def _night_low_HI_thres(self):
        return self._daytime_low_HI_thres() + self._night_shift_amount
