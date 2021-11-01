from typing_extensions import TypeAlias
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from evaluation.operations import get_high, get_low
import matplotlib.pyplot as plt


def get_profit(x, position_params):
    if x[0] == x[1]:
        if x[2] > position_params['tp']:
            return position_params['tp'] - position_params['spread']
        elif x[2] < -position_params['sl']:
            return -position_params['sl']
        else:
            return x[2] - position_params['spread'] if x[2] > position_params['spread'] else x[2]
    elif x[0] > x[1]:
        return -position_params['sl']
    else:
        return position_params['tp'] - position_params['spread']

def get_eval_fces(type, position_params):
    if type == 'long':
        return (lambda high_diff: get_high(high_diff, position_params['tp']),
        lambda low_diff: get_low(low_diff, position_params['sl']),
        lambda high, low: (high, low),
        lambda open_price, open_tail_price : (open_tail_price - open_price)*position_params['points'])
    else:
        return (lambda low_diff: get_low(low_diff, position_params['tp']),
        lambda high_diff: get_high(high_diff, position_params['sl']),
        lambda high, low: (low, high),
        lambda open_price, open_tail_price : (open_price - open_tail_price)*position_params['points'])

def add_profit_along_time(pair_timeseries, position_params):
    points = position_params['points']
    observe = position_params['observe']
    high_price_win = sliding_window_view(pair_timeseries['High'].values, window_shape = observe)[:-2]
    low_price_win = sliding_window_view(pair_timeseries['Low'].values, window_shape = observe)[:-2]
    open_price = pair_timeseries['Open'].values[:-observe-1]
    open_tail_price = pair_timeseries['Open'].values[observe+1:]

    open_price = open_price.reshape(open_price.shape[0],1)

    open_to_high = np.concatenate(
            [open_price, high_price_win], axis=1)
    open_to_low = np.concatenate(
            [open_price, low_price_win], axis=1)
    open_to_high = np.apply_along_axis(lambda x: (x - x[0])*points, 1, open_to_high)
    open_to_low = np.apply_along_axis(lambda x: (x - x[0])*points, 1, open_to_low)

    get_tp, get_sl, get_correct_diffs, get_open_tail_diffs = get_eval_fces('long', position_params)
    diffs_for_tp, diffs_for_sl = get_correct_diffs(open_to_high, open_to_low)
    
    open_tail_price = (open_tail_price - open_price)*points
    open_tail_price = open_tail_price.reshape(open_tail_price.shape[0],1)

    tp_arr = np.apply_along_axis(lambda x: get_tp(x), 1, diffs_for_tp).reshape(diffs_for_tp.shape[0],1)
    sl_arr = np.apply_along_axis(lambda x: get_sl(x), 1, diffs_for_sl).reshape(diffs_for_sl.shape[0],1)
    profit = np.apply_along_axis(lambda x: get_profit(x, position_params), 1, np.concatenate([tp_arr, sl_arr, open_tail_price], axis=1))
class Evaluator:
    def __init__(self, pair_timeseries, position_params):
        self.pair_timeseries = add_profit_along_time(pair_timeseries, position_params)
