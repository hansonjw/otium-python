import sqlite3
import pandas as pd

import click
from flask import Flask, current_app, g, flash
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    db.create_all(app=app)

# models, helper functions, etc.

def getCycleNormData():
    qry = CycleNormData.query
    dfQry=pd.read_sql(qry.statement,qry.session.bind)
    dfQry.set_index('normDate', inplace=True)
    return dfQry

def getCycleDates():
    qry = CycleDates.query
    dfQry = pd.read_sql(qry.statement, qry.session.bind)
    dfQry.set_index('index', inplace=True)
    return dfQry

class CycleDates(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    peak = db.Column(db.DateTime)
    bottom = db.Column(db.DateTime)
    recovery = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    crash = db.Column(db.Integer)
    decline =  db.Column(db.Float)
    title = db.Column(db.String)

# This table stores normalized data for each cycle...this is kind of ugly, do I really want this?
class CycleNormData(db.Model):
    normDate = db.Column(db.Integer, primary_key=True)
    Jun_1950 = db.Column(db.Float)
    Jan_1953 = db.Column(db.Float)
    Sep_1955 = db.Column(db.Float)
    Aug_1956 = db.Column(db.Float)
    Aug_1959 = db.Column(db.Float)
    Dec_1961 = db.Column(db.Float)
    Feb_1966 = db.Column(db.Float)
    Sep_1967 = db.Column(db.Float)
    Nov_1968 = db.Column(db.Float)
    Jan_1973 = db.Column(db.Float)
    Nov_1980 = db.Column(db.Float) 
    Oct_1983 = db.Column(db.Float)
    Aug_1987 = db.Column(db.Float)
    Oct_1989 = db.Column(db.Float) 
    Jul_1990 = db.Column(db.Float)
    Oct_1997 = db.Column(db.Float)
    Jul_1998 = db.Column(db.Float)
    Jul_1999 = db.Column(db.Float)
    Mar_2000 = db.Column(db.Float)
    Oct_2007 = db.Column(db.Float)
    May_2015 = db.Column(db.Float)
    Jan_2018 = db.Column(db.Float)
    Sep_2018 = db.Column(db.Float)
    Feb_2020 = db.Column(db.Float)
