import sys

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

def get_timeseries_product(pair_timeseries, observe):
    high_price_win = sliding_window_view(pair_timeseries['High'].values, window_shape = observe)[:-2]
    low_price_win = sliding_window_view(pair_timeseries['Low'].values, window_shape = observe)[:-2]
    open_price = pair_timeseries['Open'].values[:-observe-1]
    open_tail_price = pair_timeseries['Open'].values[observe+1:]
    return high_price_win, low_price_win, open_price, open_tail_price

def get_diffs_from_windows(points, open_price, high_price_win, low_price_win):
    open_price = open_price.reshape(open_price.shape[0],1)
    open_to_high = np.concatenate(
            [open_price, high_price_win], axis=1)
    open_to_low = np.concatenate(
            [open_price, low_price_win], axis=1)
    open_to_high = np.apply_along_axis(lambda x: (x - x[0])*points, 1, open_to_high)
    open_to_low = np.apply_along_axis(lambda x: (x - x[0])*points, 1, open_to_low)
    return open_to_high, open_to_low

def add_profit_along_time(data_for_profit, position_params, position_type):
    get_tp, get_sl, get_correct_diffs, get_open_tail_diffs = get_eval_fces(position_type, position_params)
    open_price, open_to_high, open_to_low, open_tail_price = data_for_profit
    open_tail_diff = get_open_tail_diffs(open_price, open_tail_price)
    open_tail_diff = open_tail_diff.reshape(open_tail_diff.shape[0],1)
    diffs_for_tp, diffs_for_sl = get_correct_diffs(open_to_high, open_to_low)
    tp_arr = np.apply_along_axis(lambda x: get_tp(x), 1, diffs_for_tp).reshape(diffs_for_tp.shape[0],1)
    sl_arr = np.apply_along_axis(lambda x: get_sl(x), 1, diffs_for_sl).reshape(diffs_for_sl.shape[0],1)
    return np.apply_along_axis(lambda x: get_profit(x, position_params), 1, np.concatenate([tp_arr, sl_arr, open_tail_diff], axis=1))
class Evaluator:
    def __init__(self, pair_timeseries, position_params):
        observe = position_params['observe']
        points = position_params['points']
        high_price_win, low_price_win, open_price, open_tail_price = get_timeseries_product(pair_timeseries, observe)
        open_to_high, open_to_low = get_diffs_from_windows(points, open_price, high_price_win, low_price_win)
        data_for_profit = (open_price, open_to_high, open_to_low, open_tail_price)
        self.pair_timeseries = pair_timeseries[:-(observe+1)]
        self.pair_timeseries = self.pair_timeseries.assign(long=add_profit_along_time(data_for_profit, position_params, 'long'))
        self.pair_timeseries = self.pair_timeseries.assign(short=add_profit_along_time(data_for_profit, position_params, 'short'))
        print(self.pair_timeseries)

    # def get_evaluation_values(requirements):
    def get_positions_profits(self, positions_indexies, position_type):
        return self.pair_timeseries.loc[positions_indexies, position_type]

    def get_mean(self, profits):
        df_len = self.pair_timeseries.shape[0]
        return profits.sum()/df_len

    def get_profit_factor(self, profits):
        wins = profits.loc[profits > 0].sum()
        loss = abs(profits.loc[profits < 0].sum())
        return (wins/loss) if loss != 0 else sys.maxsize

    def get_line_slope(self, profits):
        return (profits.iloc[0] - profits.iloc[-1])/(profits.index[0] - profits.index[-1])


 