import sqlite3
import pandas as pd
import yfinance as yf

import click
from flask import Flask, current_app, g, flash
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, event

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    db.create_all(app=app)

# models, helper functions, etc.

class CycleDates(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    peak = db.Column(db.DateTime)
    bottom = db.Column(db.DateTime)
    recovery = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    crash = db.Column(db.Integer)
    decline =  db.Column(db.Float)
    title = db.Column(db.String)


def getCycleDates():
    print("getCycleDates called...")
    qry = CycleDates.query
    dfQry = pd.read_sql(qry.statement, qry.session.bind)
    dfQry.set_index('index', inplace=True)
    if len(dfQry.index) < 1:
        findCycleDates()
        getCycleDates()
    else:
        pass
    return dfQry


def findCycleDates(app, decline=.1):
    # Less than ideal, but serviceable...
    # Computationally intensive, but needs to remain in the database
    with app.app_context():
        try:
            df = yf.Ticker("^GSPC").history(period="max").Close
            # df should be raw data in the form similar/same to the above line of code
            print("findCycleDates called...")

            curMax = None
            lclMax = None
            peakList = []
            bottomList = []
            durationList = []
            crashList = []
            recoveryList = []
            declineList = []
            nameList = []

            # cycle through market data and find peaks and valleys
            for idx, val in df.items():
                if (curMax is None) and (lclMax is None):
                    curMax = [idx, val]
                elif(curMax is None) and (val < lclMax[1]):
                    # in a valley looking for recovery
                    pass
                elif(curMax is None) and (val >= lclMax[1]):
                    # recovery found...
                    peakList.append(lclMax[0])
                    recoveryList.append(idx)
                    # ...and reset curMax to find next peak
                    curMax = [idx, val]        
                elif(val < (1.0-decline) * curMax[1]):
                    # peak found...
                    lclMax = curMax
                    curMax=None
                elif(val > curMax[1]):
                    # Not in valley and peak not found yet...
                    curMax = [idx, val]
                else:
                    pass
            
            # populate lists
            for i in range(len(peakList)):
                data = df[ peakList[i] : recoveryList[i] ]
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
        except:
            error = "database error from findCycleDates method"
            print(errror)

    return cycleData