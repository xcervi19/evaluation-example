# Written by Karel Cervicek <cervicekkarel@gmail.com>, 1993
import sys
import getopt
import pandas as pd
import numpy as np
import config as c
from evaluation.Evaluator import Evaluator

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "o:", ["operation="])
    except getopt.GetoptError:
        print('-o --operation')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-o", "--operation"):
            operation = arg

    if operation == 'test':
        pair_timeseries = pd.read_csv(c.PAIR_CSV, sep=',', header=0, usecols=c.PAIR_COLS)
        positions = pd.read_csv(c.POSITIONS_CSV, sep=',', header=0, usecols=c.POSITIONS_COLS)

        evaluator = Evaluator(pair_timeseries, c.POSITION_PARAMS)
        profits = evaluator.get_positions_profits((positions.index[positions['bool'] == 1]).tolist(), 'long')
        mean = evaluator.get_mean(profits)
        factor = evaluator.get_profit_factor(profits)
        slope = evaluator.get_line_slope(np.cumsum(profits), profits.index)
        max_lost = evaluator.get_max_lost(profits)
        rvalue = evaluator.get_line_rvalue(np.cumsum(profits), profits.index, slope)
        print(np.sum(profits))
        print(mean)
        print(factor)
        print(slope)
        print(max_lost)
        print(rvalue)
if __name__ == "__main__":
    main(sys.argv[1:])
