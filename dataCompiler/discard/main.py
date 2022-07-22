# import yfinance
import yfinance as yf
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine

# Some output controls/options:
pd.set_option("display.max_rows", None, "display.max_columns", None)
# pd.options.mode.chained_assignment = None


# establish connection to yfinance and get raw data
def getRawData(ticker = "^GSPC"):
    rawHistory = yf.Ticker(ticker).history(period="max")
    idx= pd.date_range(rawHistory.index[0], rawHistory.index[-1])
    df = rawHistory.reindex(idx, method='ffill')
    print("THIS IS THE RAW DATA: ", df)
    return df


def getAnnualReturns(df):
    # generate list of unique years represented in passed-in data df
    mrktData=df.Close
    years = mrktData.index.year.unique()

    # create empty lists for Year, start date, finish date, and return calculation
    y = []
    s = []
    f = []
    r = []

    # fill in empty lists through manipulation of passed in pandas dataframe
    for year in years:
        y.append(int(year))
        t = mrktData[str(year)]
        s.append(round(t[0], 1))
        f.append(round(t[-1], 1))
        r.append(round( (100*((t[-1])/t[0] - 1)), 1))

    # create dictionary of year, start date, finish date and return calculation
    dict = {'year':y, 'start':s, 'finish':f, 'annReturn':r}

    # convert dictionary to pandas dataframe
    annDf = pd.DataFrame.from_dict(dict)

    # write dataframe to database...
    engine = create_engine('sqlite:///./../../instance/otium.db', echo = False)
    annDf.to_sql('annual_returns', con=engine, if_exists='replace')

    return annDf


# pass in a python pandas dataFrame
def findCycles(df, decline):
    mrktData = df.Close

    curMax = None
    lclMax = None
    peakList = []
    bottomList = []
    durationList = []
    crashList = []
    recoveryList = []
    declineList = []
    nameList = []

    for idx, val in mrktData.items():
        if (curMax is None) and (lclMax is None):
            curMax = [idx, val]
        elif(curMax is None) and (val < lclMax[1]):
            # in a valley looking for recovery
            pass
        elif(curMax is None) and (val >= lclMax[1]):
            peakList.append(lclMax[0])
            recoveryList.append(idx)
            # ...and reset curMax to find next peak
            curMax = [idx, val]        
        elif(val < (1.0-decline) * curMax[1]):
            # peak found...
            lclMax = curMax
            curMax=None
        elif(val > curMax[1]):
            # peak not found yet...
            curMax = [idx, val]
        else:
            pass

    for i in range(len(peakList)):
        data = mrktData[ peakList[i] : recoveryList[i] ]
        bottomList.append(data.idxmin())
        durationList.append( (recoveryList[i] - peakList[i]).days )
        crashList.append( (data.idxmin() - peakList[i]).days )
        decline = 100 * (data.min() - data[ peakList[i] ]) / data[ peakList[i] ]
        declineList.append(decline)
        nameList.append(peakList[i].strftime("%b_%Y"))

    # create DataFrame
    cycleData = pd.DataFrame({'peak':peakList, 'bottom':bottomList,'recovery':recoveryList, 'crash': crashList, 'duration': durationList, 'decline': declineList, 'title':nameList})

    # write to database...
    engine = create_engine('sqlite:///./../instance/otium.db', echo = False)
    cycleData.to_sql('cycle_dates', con=engine, if_exists='replace')

    return cycleData


# pass in a python pandas dataFrame
def createCycleData(df, cyDf):
    mrktData = df.Close
    # extract columns relevant columns and convert to lists for iteration
    peaks = cyDf.peak.tolist()
    rcvrs = cyDf.recovery.tolist()
    titles = cyDf.title.tolist()

    l = len(peaks)

    dfList = []
    for i in range(l):
        data = (mrktData[peaks[i] : rcvrs[i]])
        title = titles[i]
        val0 = mrktData[peaks[i]]
        day0 = peaks[i]
        
        normVals = data.apply(lambda x: x/val0).to_frame()
        normVals.reset_index(inplace=True)
        normVals.rename(columns = {'index':'Date'}, inplace=True)
        normVals['normDate'] = (normVals.Date-day0).dt.days
        normVals1 = normVals.set_index('normDate')
        cycleData = normVals1.rename({'Close': title}, axis=1)

        dfList.append(cycleData[title])
    cycleData = pd.concat(dfList, axis=1)
    cycleData.sort_index(inplace=True)

    # write to database...
    engine = create_engine('sqlite:///./../instance/otium.db', echo = False)
    cycleData.to_sql('cycle_norm_data', con=engine, if_exists='replace')

    return cycleData


def formatYearWeek(s):
    if len(s) < 7:
        s = s.split('-')[0] + '-0' + s.split('-')[1]
    else:
        pass
    return s

def weeklyHiLow(df):
    highLow = df[['High', 'Low']]

    ## Year, Week, and Year_Week
    ## https://en.wikipedia.org/wiki/ISO_week_date#First_week
    highLow['week'] = highLow.index.isocalendar().week
    highLow['year'] = highLow.index.isocalendar().year
    highLow['year_week'] = highLow['year'].astype(str) + "-" + highLow['week'].astype(str)
    highLow['year_week'] = highLow['year_week'].apply(lambda x: formatYearWeek(x))

    ## Munge data for weekly Highs
    highLow['wkHigh'] = highLow.groupby('year_week')['High'].transform('max')
    highLow['isWkHigh'] = (highLow['wkHigh'] == highLow['High'])
    highLow['wkHighDate'] = highLow.index
    hs = highLow.loc[highLow['isWkHigh'] == True, ['wkHigh', 'wkHighDate', 'year_week']]
    hs.set_index('year_week', inplace = True)
    hSt = hs['wkHigh'][0]
    hs['wkHighNorm'] = hs['wkHigh'].apply(lambda x: round(x/hSt, 4))

    ## Munge data for weekly Lows
    highLow['wkLow'] = highLow.groupby('year_week')['Low'].transform('min')
    highLow['isWkLow'] = (highLow['wkLow'] == highLow['Low'])
    highLow['wkLowDate'] = highLow.index
    ls = highLow.loc[highLow['isWkLow'] == True, ['wkLow', 'wkLowDate', 'year_week']]
    ls.set_index('year_week', inplace = True)
    lSt = ls['wkLow'][0]
    ls['wkLowNorm'] = ls['wkLow'].apply(lambda x : round(x/lSt, 4))

    ## Combine Highs and Lows into one data set
    highLowClean = hs.merge(ls, left_on='year_week', right_on='year_week')

    # write to database...
    engine = create_engine('sqlite:///./../instance/otium.db', echo = False)
    highLowClean.to_sql('weekly', con=engine, if_exists='replace')

    return(highLowClean)


def growthRatesInterval(df, spanYrs):
    startShifted = df.index[0] + relativedelta(years=spanYrs)
    start = df.index[0]
    endShifted = df.index[-1] - relativedelta(years=spanYrs)
    end = df.index[-1]

    df1 = df[start:endShifted].reset_index().rename(columns={'index':'dateStart', 'Close':'valStart'})
    df2 = df[startShifted:end].reset_index().rename(columns={'index':'dateEnd', 'Close':'valEnd'})

    df3 = pd.concat([df1, df2], axis=1)

    df3['CAGR'] = 100*( (df3['valEnd']/df3['valStart'])**(1/(((df3['dateEnd'] - df3['dateStart']).dt.days)/365)) -1)

    return df3




# Code execution
# print(getAnnualReturns(getRawData()))
# c = findCycles(getRawData(), decline=0.1)
# d = createCycleData(getRawData(), c)
# print("...here is the dataframe")
# print(d)
test = weeklyHiLow(getRawData())
print(test)

# x = growthRatesInterval(getRawData(), 5)
# print(x)