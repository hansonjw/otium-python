import datetime
import yfinance as yf
import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from otium.db import db, getCycleDates, findCycleDates


class indexData():
        
    def __init__(self):
        self._lastUpdate = None
        self._rawData = None
        self._normData = None
        self._annualReturns = None
        self._cycleDates = None
        self._cycleData = None
        self.updateAll()

    # 
    # Setter functions
    # 

    def set_rawData(self, start=None, end=None, ticker = "^GSPC"):
        if start is None or end is None:
            self._rawData = yf.Ticker(ticker).history(period="max").Close
        else:
            self._rawData = self._rawData.append(yf.Ticker(ticker).history(start=start, end=end).Close)
        return

    def set_normData(self):
        startVal = self._rawData[0]
        
        idx = pd.date_range('1950-01-01', self.get_today())
        df = self._rawData.reindex(idx, method='ffill').fillna(startVal)
        
        self._normData = (df/startVal).to_frame()

        cagr = 365 * ((self._normData['Close'][-1])**(1/len(self._normData.index)) - 1)
        growthCurve = []
        growthCurveLow = []
        growthCurveHigh = []
        for n in range(len(self._normData.index)):
            growthCurve.append((1 + cagr/365)**n)
            growthCurveLow.append((1 + (cagr-.005)/365)**n)
            growthCurveHigh.append((1 + (cagr+.005)/365)**n)
        self._normData['growth'] = growthCurve
        self._normData['growthLow'] = growthCurveLow
        self._normData['growthHigh'] = growthCurveHigh

        # 10, 20, 30 year CAGR calculations
        self._normData['10'] = self._normData["Close"].shift(365*10)
        self._normData['20'] = self._normData["Close"].shift(365*20)
        self._normData['30'] = self._normData["Close"].shift(365*30)

        self._normData['10 CAGR'] = round(((self._normData['Close']/self._normData['10'])**(1/10) - 1) * 100, 2)
        self._normData['20 CAGR'] = round(((self._normData['Close']/self._normData['20'])**(1/20) - 1) * 100, 2)
        self._normData['30 CAGR'] = round(((self._normData['Close']/self._normData['30'])**(1/30) - 1) * 100, 2)

        #  CAGR since start/1950...
        self._normData['1950 CAGR'] = cagr*100

        return
    
    def set_annualReturns(self):
        years = self._rawData.index.year.unique()

        # create empty lists for Year, start date, finish date, and return calculation
        y = []
        s = []
        f = []
        r = []

        # fill in empty lists through manipulation of passed in pandas dataframe
        for year in years:
            y.append(int(year))
            t = self._rawData[str(year)]
            s.append(round(t[0], 1))
            f.append(round(t[-1], 1))
            r.append(round((100*((t[-1])/t[0] - 1)), 1))

        # create dictionary of year, start date, finish date and return calculation
        # convert dictionary to pandas dataframe
        self._annualReturns = pd.DataFrame.from_dict({'year':y, 'start':s, 'finish':f, 'annReturn':r})

    def set_lastUpdate(self):
        self._lastUpdate = self.get_today()
        return

    def updateAll(self):
        if self._lastUpdate is None:
            self.set_rawData()
            self.set_normData()
            self.set_lastUpdate()
            self.set_annualReturns()
            # self.set_cycleDates()
            # self.set_cycleData()
        elif self.get_today() > self._lastUpdate:
            self.set_rawData(start = self._lastUpdate, end=self.get_today())
            self.set_normData()
            self.set_lastUpdate()
            self.set_annualReturns()
            # self.set_cycleDates()
            # self.set_cycleData()
        else:
            # print("update not needed")
            pass
        return

    # 
    # Getter functions
    # 

    def get_today(self):
        return datetime.date.today()

    def get_rawData(self):
        self.updateAll()
        return self._rawData

    def get_normData(self):
        self.updateAll()
        return self._normData

    def get_annualReturns(self):
        self.updateAll()
        return self._annualReturns

    #
    #
    # Cycle Data Methods (work in Progress)

    def set_cycleDates(self, cycDates):
        self._cycleDates = cycDates
        return
    
    def get_cycleDates(self):
        return self._cycleDates

    def set_cycleData(self, cycDates):
        self._cycleDates = cycDates
        # get cycle dates from database, extract relevant columns, and convert to lists for iteration
        d = self._cycleDates
        peaks = d.peak.tolist()
        rcvrs = d.recovery.tolist()
        titles = d.title.tolist()
        # here is where I can deal with duration...

        dfList = []
        for i in range(len(peaks)):
            data = (self.get_rawData()[peaks[i] : rcvrs[i]])
            title = titles[i]
            val0 = data[peaks[i]]
            day0 = peaks[i]
            newIndex = pd.date_range(start=peaks[i], end=rcvrs[i], freq='D')

            normVals = data.apply(lambda x: x/val0).to_frame().reindex(newIndex, method='ffill')

            normVals.rename(columns = {'index':'Date'}, inplace=True)
            normVals['normDate'] = (normVals.index-day0).days
            normVals1 = normVals.set_index('normDate')
            cycleData = normVals1.rename({'Close': title}, axis=1)

            dfList.append(cycleData[title])
        cycleData = pd.concat(dfList, axis=1)
        cycleData.sort_index(inplace=True)

        # set object item...
        self._cycleData = cycleData
        
        return

    def get_cycleData(self, cycDates):

        if (cycDates.equals(self._cycleDates)) and (self._cycleData is not None):
            pass
        else:
            self.set_cycleData(cycDates)

        self.updateAll()
        return self._cycleData



