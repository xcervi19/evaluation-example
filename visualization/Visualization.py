
# Copyright (C) KM soft s.r.o - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Karel Cervicek <ecervicekkarel@gmail.com>, 1993

# example !
'''
        dataForPlot = {
            "series": [[ff.loc[:, 'Close']], [ff.loc[:, '1']]],
            "plot_types": [['-'], ['-']],
            "plot_treshholds" :[False, '1'],
            "tresholds" :splitTh,
            "fill-between": ff.loc[:, '2']
        }
        if gui.created:
            gui.updatePlot(dataForPlot, positionType)
        else:
            gui.createPlot([311, 312, 313], dataForPlot)
'''

import random
import re
import numpy as np
import string
import matplotlib.pyplot as plt
from datetime import datetime

import pandas as pd
# from matplotlib.patches import Rectangle
import matplotlib.patches as patches
import EvaluationUtils as ev
from BlitManager import BlitManager
from mplfinance.original_flavor import candlestick2_ohlc
import matplotlib.dates as mpl_dates
from Utils import reduceSplitTh

class Visualization(object):

    def __init__(self):
        self.created = False
        self.plotCandles = False
    # https://matplotlib.org/tutorials/introductory/sample_plots.html

    def createPlot(self, figs, data):
        fig = plt.figure(figsize=(20, 8))
        fig.tight_layout()
        plt.subplots_adjust(wspace=0, hspace=0)
        if data['plot_whole_df']:
            self.plotCandles = True
            dataFrame = data['time_df']

            # ohlc = dataFrame.loc[:, ['Time', 'Open', 'High', 'Low', 'Close']]
            # ohlc['Time'] = pd.to_datetime(ohlc['Time'])
            # ohlc['Time'] = ohlc['Time'].apply(mpl_dates.date2num)
            # ohlc = ohlc.astype(float)

            def isInMeanTolerance(col):
                firstSr = dataFrame.loc[:, col]
                firstSrMean = firstSr.mean()
                ratio = refMean/firstSrMean
                return True if ratio > 0.5 and ratio < 4 else False

            def isNotSplit(col):
                firstSr = dataFrame.loc[:, col]
                new = firstSr[(firstSr != 1) & (firstSr != 0)]
                return False if new.empty else True
                
            def getTreshholdInDimensions(col, tresholds):
                if col in tresholds:
                    return tresholds[col]
                else:
                    return False

            cols = [c for c in dataFrame.columns if c not in ['Time', 'Open', 'High', 'Low', 'bool']]
            cols = list(filter(isNotSplit, cols))
            cols.reverse()

            outerSeries = []
            while cols:
                colRef = cols.pop()
                if outerSeries and [ True for s in outerSeries if colRef in s]:
                    continue
                innerHead = [colRef]
                refMean = firstSr = dataFrame.loc[:, colRef].mean()
                inner = list(filter(isInMeanTolerance, cols))
                outerSeries.append(innerHead+inner)

            seriesMulti = list(map(lambda x: list(map(lambda y: dataFrame.loc[:, y], x)), outerSeries))
            plotTypesMulti = list(map(lambda x: list(map(lambda y: '-', x)), outerSeries))
            seriesMultiLen = len(seriesMulti)

            splitTh = reduceSplitTh(data['formula'], data['time_df'])
            seriesMultiTreshholds = list(map(lambda x: list(map(lambda y: getTreshholdInDimensions(y, splitTh), x)), outerSeries))
            figs = [[seriesMultiLen, 1, i+1] for i in range(seriesMultiLen)]
            if not splitTh:
                print('WARMING >>> empty split, something is wrong')

        else:
            seriesMulti = data['series']
            plotTypesMulti = data['plot_types']
            ths = data['tresholds'] if 'tresholds' in data else np.zeros(len(seriesMulti))
            seriesMultiTreshholds = data['plot_treshholds'] if 'plot_treshholds' in data else np.zeros(len(seriesMulti))
        #TODO: show startPositionInd as axvline PART 1 ???
        # crossValue = data['value-cross-lines'] if 'value-cross-lines' in data else []
        # crossIdx = data['idx-cross-lines'] if 'idx-cross-lines' in data else []
        # startPositionInd = ev.getPosStart(crossValue)
        # startPositionInd = np.concatenate((startPositionInd, crossIdx)) 

        self.axis = []
        self.lns = []
        print(seriesMultiTreshholds)
        for subfig, series, plotTypes, thsFlag in zip(figs, seriesMulti, plotTypesMulti, seriesMultiTreshholds):
            ax = fig.add_subplot(*subfig, sharex=self.axis[0] if self.axis else None)
            if len(self.axis) == 0 and self.plotCandles:
                (lineCollection, barCollection) = candlestick2_ohlc(ax,dataFrame['Open'], dataFrame['High'], dataFrame['Low'], dataFrame['Close'],width=0.6)
            self.axis.append(ax)
            index = np.arange(len(series[len(series) - 1]))
            localLns = []
            for vector, lineType, treshold in zip(series, plotTypes, thsFlag):
                (ln,) = ax.plot(index, vector, lineType, alpha=0.5, animated=True)
                localLns.append(ln)
                if treshold:
                    ax.axhline(treshold, color='green', lw=2, alpha=0.7)
                    ax.fill_between(index, vector.max(), vector.min(), where = vector > treshold, color='green', alpha=0.3)
             #TODO: show startPositionInd as axvline PART 2 ???
            # for xc in startPositionInd:
            #     ax.axvline(x=xc)
            self.lns = self.lns + localLns
        for ax in self.axis[:-1]:
            ax.xaxis.set_visible(False)
        self.fr_number = ax.annotate(
            "0",
            (0, 1),
            xycoords="axes fraction",
            xytext=(10, -10),
            textcoords="offset points",
            ha="left",
            va="top",
            animated=True,
        )
        artists = self.axis + self.lns + [self.fr_number] #+ lineCollection + barCollection
        # print(artists)
        self.bm = BlitManager(fig.canvas, artists)
        self.created = True
        # make sure our window is on the screen and drawn
        plt.show(block=False)
        plt.pause(.1)

    def updatePlot(self, data, pair):
        return
        # plt.xlim(0, len(data[1]))
        # plt.ylim(X.min()*0.99, X.max()*1.01)
        # plt.plot(np.arange(len(X)), X, 'k:', alpha=0.5)
        # plt.plot(np.arange(len(X))[pivots != 0], X[pivots != 0], 'k-')
        # plt.scatter(np.arange(len(X))[pivots == 1], X[pivots == 1], color='g')
        # plt.scatter(np.arange(len(X))[pivots == -1], X[pivots == -1], color='r')
        # plt.show()

        seriesMulti = data['series']
        ths = data['tresholds'] if 'tresholds' in data else []
        plotThsFlags = data['plot_treshholds'] if 'plot_treshholds' in data else []
        startPositionInd = ev.getPosStart(data['value-cross-lines']) if 'value-cross-lines' in data else []
        startPositionInd = np.concatenate((startPositionInd,data['idx-cross-lines'] if 'idx-cross-lines' in data else []))
        bool = data['fill-between'].values if 'tresholds' in data else []

        for i, series in enumerate(seriesMulti):
            totalMax = float('-inf')
            totalMin = float('inf')
            index = np.arange(len(series[len(series) - 1]))
            for s in series:
                if s.max() > totalMax:
                    totalMax = s.max()
                if s.min() < totalMin:
                    totalMin = s.min()
            self.fr_number.set_text("frame: {j}".format(j=pair))
            self.axis[i].set_ylim([totalMin, totalMax])
            self.axis[i].set_xlim([0, len(series[0])])
            self.axis[i].collections.clear()
            if len(plotThsFlags) and plotThsFlags[i]:
                self.axis[i].fill_between(index, totalMax, totalMin, where = bool < ths[plotThsFlags[i]], color='green', alpha=0.3)
            for j, s in enumerate(series):
                self.lns[i+j].set_xdata(np.arange(len(s)))
                self.lns[i+j].set_ydata(s)

            self.bm.update()
        plt.pause(0.1)
