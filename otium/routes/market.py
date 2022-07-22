import base64
from io import BytesIO
import matplotlib.pyplot as plt
# yfinance stuff to get market data
import yfinance as yf
from flask import Flask
from matplotlib.figure import Figure
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from otium.db import db, getCycleDates
from otium.routes.plotCharts.chartFuncs import colorDictObj, todayPlot, histPlot, deltaGrowthPlot, allCycles, shortCycles, medCycles, longCycles, barAnnual, growthRates
import datetime
import pandas as pd


# Will this idea work??  Key functionality...all the routes below should be working with this...updating, modifying, plotting data within, etc.
from otium.routes.plotCharts.chartData import indexData
obj = indexData()


bp = Blueprint('market', __name__, url_prefix='/')


@bp.route('/')
def index():

    # get end date of prior cycle
    ep = getCycleDates()['recovery'].iloc[-1]
    e = datetime.date.today() + datetime.timedelta(days=1)

    # find start date of current cycle (between ep, and e), and reslice data, and renormalize
    d1 = obj.get_normData().Close[ ep:e ]
    s = d1.idxmax()
    d2 = d1[s:e] / d1[s]

    data = [todayPlot(d2)]

    return render_template('market/today.html', data=data)


@bp.route('/history')
def history():
    data = [ histPlot(obj.get_normData()), barAnnual(obj.get_annualReturns()) ]
    return render_template('market/history.html', data = data)


@bp.route('/cycles')
def cycles():

    # All of this logic could be redone, but let's just get the site up and running
    cycDf = getCycleDates()
    colorObj = colorDictObj(cycDf)
    # pass in cycDf, check if obj._cycleDates is equal to cycDf, if so get cycleData, otherwise recalc
    df = obj.get_cycleData(cycDf)
    # add logic regarding current cycle state?

    # Plot current cycle...
    # get, condition, and append current data...
    curStart = cycDf.recovery.max()
    curEnd = datetime.date.today() + datetime.timedelta(days=1) 
    tmpData = yf.Ticker("^GSPC").history(start=curStart, end=curEnd).Close
    maxDate = tmpData.idxmax()
    maxVal = tmpData.max()
    curData = tmpData[ maxDate : curEnd ]
    curDataNorm = curData.apply(lambda x: (x/maxVal) )

    curDataDf = pd.concat( {"raw": curData, "norm": curDataNorm}, axis=1)
    curDataDf.reset_index(inplace=True)
    curDataDf['normDate'] = (curDataDf.Date - maxDate).dt.days
    curDataDf.set_index('normDate', inplace=True)
    
    df['current'] = curDataDf.norm
    df.current.backfill(inplace=True)

    # chart calls...
    data1 = allCycles(df, cycDf, colorObj)
    data2 = shortCycles(df, cycDf, colorObj)
    data3 = medCycles(df, cycDf, colorObj)
    data4 = longCycles(df, cycDf, colorObj)

    # pass list of chart calls into html template to render on screen...
    data = [data1, data2, data3, data4]
    return render_template('market/cycles.html', data = data)


@bp.route('/cagr')
def cagr():
    data = [ histPlot(obj.get_normData(), growth=True), histPlot(obj.get_normData(), growth=True, log=True), growthRates(obj.get_normData()) ]
    return render_template('market/cagr.html', data = data)