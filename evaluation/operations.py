import numpy as np

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

def getWindowSum(sr, WindowLn):
    return sr.rolling(window=WindowLn).apply(
        lambda x: x.sum(), raw=True)