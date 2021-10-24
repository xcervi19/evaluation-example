# Written by Karel Cervicek <cervicekkarel@gmail.com>, 1993
import sys
import getopt
import pandas as pd
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

        Evaluator(pair_timeseries, c.POSITION_PARAMS)
if __name__ == "__main__":
    main(sys.argv[1:])
