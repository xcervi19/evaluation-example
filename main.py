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

        positions_indexies = (positions.index[positions['bool'] == 1]+5).tolist()
        profits = evaluator.get_positions_profits(positions_indexies, 'long')
        mean = evaluator.get_mean(profits)
        factor = evaluator.get_profit_factor(profits)
        max_lost = evaluator.get_max_lost(profits)

        slope = evaluator.get_line_slope(np.cumsum(profits), profits.index)
        rvalue = evaluator.get_line_rvalue(np.cumsum(profits), profits.index, slope)
        line_sq_error = evaluator.get_line_sq_error(np.cumsum(profits),profits.index, slope)

        positions_step_mean = evaluator.get_positions_step_mean(positions_indexies)
        positions_step_std = evaluator.get_positions_step_std(positions_indexies)

        print('mean')
        print(mean)
        print('factor')
        print(factor)
        print('max_lost')
        print(max_lost)
        print('slope')
        print(slope)
        print('rvalue')
        print(rvalue)
        print('line_sq_error')
        print(line_sq_error)
        print('positions_step_mean')
        print(positions_step_mean)
        print('positions_step_std')
        print(positions_step_std)

        positions_rows = evaluator.build_description_matrix(positions_indexies, 'long')
        print(positions_rows)


if __name__ == "__main__":
    main(sys.argv[1:])
