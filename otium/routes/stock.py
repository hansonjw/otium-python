import base64
from io import BytesIO

# yfinance stuff to get market data
import yfinance as yf

from flask import Flask
from matplotlib.figure import Figure

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from otium.db import db

bp = Blueprint('stock', __name__, url_prefix='/stock')


@bp.route('/', methods=('GET', 'POST'))
def index():
    error=None
    if request.method == 'POST':
        ticker = request.form['ticker']
        error = None

        if not ticker:
            error = 'Please enter a ticker symbol and data will be retrieved'
        
        if error is None:
            try:
                pass
            except:
                pass
            else:
                # return render_template('stock/plotStock.html', stockData=stockData)
                return redirect(url_for('stock.secondChart', ticker=ticker))
        
    if error is not None:
        flash(error)
    
    return render_template('stock/getStock.html')


@bp.route("/firstChart")
def firstChart():
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


@bp.route("/secondChart/<ticker>", methods=('GET', 'POST'))
def secondChart(ticker=None):

    error=None
    if request.method == 'POST':
        ticker = request.form['ticker']
        error = None

        if not ticker:
            error = 'Please enter a ticker symbol and data will be retrieved'
        
        if error is None:
            try:
                pass
            except:
                pass
            else:
                # return render_template('stock/plotStock.html', stockData=stockData)
                return redirect(url_for('stock.secondChart', ticker=ticker))
        
    if error is not None:
        flash(error)
    
    # get market data for ^GSPC, should be a seperate function??
    ticker = yf.Ticker(ticker)
    historical_price = ticker.history(period="max").Close   
    info = ticker.info,
    dividends = ticker.dividends,
    major_holders = ticker.major_holders,
    financials = ticker.financials,
    cashflow = ticker.cashflow,
    balance_sheet = ticker.balance_sheet,
    earnings = ticker.earnings

    otherData = [info, dividends, major_holders, financials, cashflow, balance_sheet, earnings]

    # Generate the figure **without using pyplot**.
    fig = Figure()
    hist = fig.subplots()
    hist.plot(historical_price)
    # Save it to a temporary buffer.

    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    
    return render_template('stock/secondChart.html', data=data, stockData=ticker, otherData=otherData)

    
