import unittest
import pandas as pd
import numpy as np

import config as c
from evaluation.operations import get_high, get_low


class MainTest(unittest.TestCase):
    def setUp(self):
        self.values = np.array([0, 20, 30, 150, 30, 70, 140, 201, 30, -30, -150, -300])

    def test_get_high(self):
        self.assertEqual(get_high(self.values, 200), 7, "wrong index of high price cross 200")
        self.assertEqual(get_high(self.values, 50), 3, "wrong index of high price cross")
        self.assertEqual(get_high(self.values, 0), 1, "wrong index of high price cross")
    def test_get_low(self):
        self.assertEqual(get_low(self.values, 30), 10, "wrong index of high price cross 200")
        self.assertEqual(get_low(self.values, 500), 11, "wrong index of high price cross")
        self.assertEqual(get_low(self.values, 0), 9, "wrong index of high price cross")
if __name__ == '__main__':
    unittest.main()
