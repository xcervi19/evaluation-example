import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view


def dataForBuyProfit(self, pos, highSer, lowSer, openSer, rangeOfObserve, frameLen, setting):
    stopLossArea, takeProfitArea, buyAreaDfHigh, buyAreaDfLow, pos = self.getBuyArea(
        pos, highSer, lowSer, openSer, rangeOfObserve, frameLen)
    takeprofitIndexies = takeProfitArea.apply(
        lambda x: self.getTakeprofitIndexies(x, setting, 'long'), axis=1)
    stoplossIndexies = stopLossArea.apply(
        lambda x: self.getStoplossIndexies(x, setting, 'long'), axis=1)
    takeprofitValues = takeProfitArea.apply(
        lambda x: self.getTakeprofitValues(x, setting, 'long'), axis=1)
    stoplossValues = stopLossArea.apply(
        lambda x: self.getStoplossValues(x, setting, 'long'), axis=1)

def add_profit_along_time(pair_timeseries, position_params):
    high_price_win = sliding_window_view(pair_timeseries['High'].values, window_shape = position_params['observe'])
    low_price_win = sliding_window_view(pair_timeseries['Low'].values, window_shape = position_params['observe'])
    open_price = pair_timeseries['Open'].values[:1-position_params['observe']]
    open_price = open_price.reshape(len(open_price),1)
    open_to_high = np.concatenate(
            [open_price, high_price_win[:, 1:]], axis=1)
    open_to_low = np.concatenate(
            [open_price, low_price_win[:, 1:]], axis=1)
    print(open_to_high)


class Evaluator:
    def __init__(self, pair_timeseries, position_params):
        self.pair_timeseries = add_profit_along_time(pair_timeseries, position_params)
