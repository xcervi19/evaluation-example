import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view


def get_high(high_diff, param):
    where = np.where(high_diff > param)[0]
    if where.shape[0] != 0:
        return where[0]
    else:
        return high_diff.shape[0] - 1

def get_low(low_diff, param):
    where = np.where(-low_diff > param)[0]
    if where.shape[0] != 0:
        return where[0]
    else:
        return low_diff.shape[0] - 1

def get_eval_fces(type, position_params):
    if type == 'long':
        return (lambda high_diff: get_high(high_diff, position_params['tp']),
        lambda low_diff: get_low(low_diff, position_params['sl']))
    else:
        return (lambda low_diff: get_low(low_diff, position_params['tp']),
        lambda high_diff: get_high(high_diff, position_params['sl']))

def add_profit_along_time(pair_timeseries, position_params):
    points = position_params['points']
    observe = position_params['observe']
    high_price_win = sliding_window_view(pair_timeseries['High'].values, window_shape = observe)
    low_price_win = sliding_window_view(pair_timeseries['Low'].values, window_shape = observe)
    open_price = pair_timeseries['Open'].values[:1-observe]
    open_price = open_price.reshape(len(open_price),1)
    open_to_high = np.concatenate(
            [open_price, high_price_win[:, 1:]], axis=1)
    open_to_low = np.concatenate(
            [open_price, low_price_win[:, 1:]], axis=1)
    open_to_high = np.apply_along_axis(lambda x: (x - x[0])*points, 1, open_to_high)
    open_to_low = np.apply_along_axis(lambda x: (x - x[0])*points, 1, open_to_low)
    get_tp, get_sl = get_eval_fces('long', position_params)
    print(np.apply_along_axis(lambda x: get_tp(x), 1, open_to_high))
    print(np.apply_along_axis(lambda x: get_sl(x), 1, open_to_low))
class Evaluator:
    def __init__(self, pair_timeseries, position_params):
        self.pair_timeseries = add_profit_along_time(pair_timeseries, position_params)
