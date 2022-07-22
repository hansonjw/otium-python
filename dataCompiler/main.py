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

    # I don't think this will work in production...see nfl structure
    # Consider a POST method...need to better understand that anyways
    # 
    # create DataFrame
    cycleData = pd.DataFrame({'peak':peakList, 'bottom':bottomList,'recovery':recoveryList, 'crash': crashList, 'duration': durationList, 'decline': declineList, 'title':nameList})

    # write to database...
    engine = create_engine('sqlite:///./../instance/otium.db', echo = False)
    cycleData.to_sql('cycle_dates', con=engine, if_exists='replace')

    return cycleData


# # pass in a python pandas dataFrame
# def createCycleData(df, cyDf):
#     mrktData = df.Close
#     # extract columns relevant columns and convert to lists for iteration
#     peaks = cyDf.peak.tolist()
#     rcvrs = cyDf.recovery.tolist()
#     titles = cyDf.title.tolist()

#     l = len(peaks)

#     dfList = []
#     for i in range(l):
#         data = (mrktData[peaks[i] : rcvrs[i]])
#         title = titles[i]
#         val0 = mrktData[peaks[i]]
#         day0 = peaks[i]
        
#         normVals = data.apply(lambda x: x/val0).to_frame()
#         normVals.reset_index(inplace=True)
#         normVals.rename(columns = {'index':'Date'}, inplace=True)
#         normVals['normDate'] = (normVals.Date-day0).dt.days
#         normVals1 = normVals.set_index('normDate')
#         cycleData = normVals1.rename({'Close': title}, axis=1)

#         dfList.append(cycleData[title])
#     cycleData = pd.concat(dfList, axis=1)
#     cycleData.sort_index(inplace=True)

#     # write to database...
#     engine = create_engine('sqlite:///./../instance/otium.db', echo = False)
#     cycleData.to_sql('cycle_norm_data', con=engine, if_exists='replace')

#     return cycleData


d = getRawData()
dates = findCycles(d, .1)
# createCycleData(d, dates)

