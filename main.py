# Written by Karel Cervicek <cervicekkarel@gmail.com>, 1993
import random
import pandas as pd
import signal
import sys
import getopt
import time
import pickle
import functools
# import cProfile
import numpy as np

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "fo:", ["operation="])
    except getopt.GetoptError:
        print('-o --operation')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-o", "--operation"):
            operation = arg
        if opt in ("-f"):
            fullfilment = True

    if operation == 'test':
        pass

if __name__ == "__main__":
    # cProfile.run('main(sys.argv[1:])')
    main(sys.argv[1:])
