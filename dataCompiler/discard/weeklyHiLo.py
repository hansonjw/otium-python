# import yfinance
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

# Some output controls/options:
# pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.options.mode.chained_assignment = None


#
#
# Do we really need this? What if we don't store to a database, but rather keep it alive and update as a 'high level' variable in the app?
#
# Data Munging to get final clean Output
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

test = weeklyHiLow(rawHistory)
print(test)