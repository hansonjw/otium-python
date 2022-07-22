import base64
from io import BytesIO
# import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
import datetime
import pandas as pd


class colorDictObj:

    def __init__(self, cycDf):
        self._cycDf = cycDf
        self.colorDict = {}
        self.colorsShort = ['#B2EBF2', '#80DEEA', '#4DD0E1', '#26C6DA', '#00BCD4', '#00ACC1', '#0097A7', '#00838F', '#006064', '#84FFFF', '#18FFFF']
        self.colorsMed = ['#B9F6CA', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#388E3C', '#2E7D32', '#1B5E20']
        self.colorsLong = ['#F8BBD0', '#F06292', '#C2185B', '#880E4F']
        self.setColorDict()

    def setColorDict(self):

        s = self.colorsShort
        m = self.colorsMed
        l = self.colorsLong

        cyclesShort = self._cycDf.query('duration<=250')['title'].tolist()
        for cyc in cyclesShort:
            self.colorDict[cyc] = s.pop()

        cyclesMed = self._cycDf.query('duration>250 & duration<1000')['title'].tolist()
        for cyc in cyclesMed:
            self.colorDict[cyc] = m.pop()
        
        cyclesLong = self._cycDf.query('duration>1000')['title'].tolist()
        for cyc in cyclesLong:
            self.colorDict[cyc] = l.pop()
        return

    def getColorDict(self):
        return self.colorDict


def todayPlot(d):
    fig = Figure(figsize=(10,6))
    # fig = Figure()
    chart = fig.subplots()

    x1 = d.index
    y1 = d.values

    chart.plot(x1, y1, color='#2874A6', marker='', linewidth=1)
    chart.set_xlabel('Date')
    highDate = d.index[0]
    chart.set_title(f"S&P 500 - Since all time high on {highDate.to_pydatetime().strftime('%b %d, %Y')}")

    # Annotate Chart
    today_val = d[-1]
    start_val = d[0]
    min_val = d.min()
    today_date = d.index[-1]
    start_date = d.index[0]
    min_date = d.idxmin()
    dateF = today_date.to_pydatetime().strftime("%b %d, %Y")
    dateS = start_date.to_pydatetime().strftime("%b %d, %Y")
    dateM = min_date.to_pydatetime().strftime("%b %d, %Y")

    strToday = f"{dateF}:\n {round(today_val*100-100, 1)}%"
    strStart = f"{dateS}:\n {round(start_val*100)}%"
    strMin = f"{dateM}:\n {round(min_val*100-100, 1)}%"
    chart.text(x1[-1], y1[-1], strToday)
    chart.text(x1[0], y1[0], strStart)
    chart.text(min_date, min_val, strMin)
    chart.plot([today_date, start_date, min_date],[today_val, start_val, min_val], marker="o", linestyle="None")

    
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def histPlot(d, growth=False, log=False):
    fig = Figure(figsize=(10,6))
    chart = fig.subplots()
    x1 = d.index
    y1 = d.Close

    chart.plot(x1, y1, color='#2874A6', marker='', linewidth=0.5)

    # formatting for the chart
    chart.set_xlabel('Year-Week')
    chart.grid(True, linestyle='-')
    chart.tick_params(labelcolor='black')
    chart.set_title("S&P 500 Historical Prices")

    # If growth flag is True, growth curves will be plotted
    if growth == True:
        x2 = d.index
        y2 = d.growth
        x3 = d.index
        y3 = d.growthHigh
        x4 = d.index
        y4 = d.growthLow
        chart.plot(x2, y2, color='#E67E22', marker='', linewidth=1.0)
        chart.plot(x3, y3, color='#F8C471', marker='', linewidth=0.5)
        chart.plot(x4, y4, color='#F8C471', marker='', linewidth=0.5)

        # Annotate growth curve with rate...
        cagr = 365 * ((d['Close'][-1])**(1/len(d.index)) - 1)
        strCagr = f"CAGR: {round(cagr*100, 2)}%"
        chart.text(x2[-1], y2[-1], strCagr)

        chart.text(x3[-1], y3[-1], "+0.5%")
        chart.text(x4[-2], y4[-2], "-0.5%")


    if log == True:
        chart.set_yscale('log')
        chart.set_title("S&P 500 Historical Prices (Log Scale)")

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def deltaGrowthPlot(d):
    # Chart 3!!
    fig = Figure(figsize=(10,6))
    chart = fig.subplots()
    x1 = d.wkLowDate
    y1 = d.deltaGrowthHigh
    x2 = d.wkLowDate
    y2 = d.deltaGrowthLow

    chart.plot(x1, y1, color='blue', marker='', linewidth=0.5)
    chart.plot(x2, y2, color='orange', marker='', linewidth=0.5)

    # formatting for the chart
    chart.set_xlabel('Year-Week')
    chart.grid(True, linestyle='-')
    chart.tick_params(labelcolor='black')
    chart.set_title("")

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def allCycles(df, cycDf, colorObj):

    colors = colorObj.getColorDict()

    # chart and figure 1
    fig = Figure(figsize=(10,6))
    chart = fig.subplots()
    for col in df.drop('current', axis=1):
        chart.plot(df[col], marker='', linewidth=0.5, alpha=0.5, color=colors[col])
    chart.plot(df.current, color='black', linewidth=1.0)

    # set chart display options
    chart.legend(loc='lower right', labels=df.keys(), fontsize='xx-small')
    chart.set_xlabel('Days since Peak')
    chart.set_title("Stock Market Declines Since 1950")
    chart.axis(xmin=0, xmax=3000)
    chart.axis(ymin=.4, ymax=1)

    # Save fig/chart to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def shortCycles(df, cycDf, colorObj):

    colors = colorObj.getColorDict()
    cyclesShort = cycDf.query('duration<=250')['title'].tolist()

    fig = Figure(figsize=(10,6))
    chart = fig.subplots()
    for cyc in cyclesShort:
        chart.plot(df[cyc], marker='', linewidth=1.0, alpha=0.5, color=colors[cyc])
    chart.plot(df.current, color='black', linewidth=1.0)

    cyclesShort.append('Current')

    # set chart display options
    chart.legend(loc='lower right', labels=cyclesShort, fontsize='xx-small')
    chart.set_xlabel('Days since Peak')
    chart.set_title("Short Term Stock Market Cycles")
    chart.axis(xmin=0, xmax=300)
    chart.axis(ymin=.4, ymax=1)

    # Save fig/chart to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
   
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def medCycles(df, cycDf, colorObj):

    colors = colorObj.getColorDict()
    cyclesMed = cycDf.query('duration>250 & duration<1000')['title'].tolist()

    fig = Figure(figsize=(10,6))
    chart = fig.subplots()
    for cyc in cyclesMed:
        chart.plot(df[cyc], marker='', linewidth=1.0, alpha=0.5, color=colors[cyc])
    chart.plot(df.current, color='black', linewidth=1.0)

    cyclesMed.append('Current')

    # set chart display options
    chart.legend(loc='lower right', labels=cyclesMed, fontsize='xx-small')
    chart.set_xlabel('Days since Peak')
    chart.set_title("Medium Term Stock Market Cycles")
    chart.axis(xmin=0, xmax=1000)
    chart.axis(ymin=.4, ymax=1)

    # Save fig/chart to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def longCycles(df, cycDf, colorObj):

    colors = colorObj.getColorDict()
    cyclesLong = cycDf.query('duration>1000')['title'].tolist()

    fig = Figure(figsize=(10,6))
    chart = fig.subplots()
    for cyc in cyclesLong:
        chart.plot(df[cyc], marker='', linewidth=1.0, alpha=0.5, color=colors[cyc])
    chart.plot(df.current, color='black', linewidth=1.0)

    cyclesLong.append('Current')

    # set chart display options
    chart.legend(loc='lower right', labels=cyclesLong, fontsize='xx-small')
    chart.set_xlabel('Days since Peak')
    chart.set_title("Long Term Stock Market Cycles")
    chart.axis(xmin=0, xmax=3000)

    # Save fig/chart to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def barAnnual(df):

    #plot bar chart
    fig = matplotlib.figure.Figure(figsize=(10,6))
    # matplotlib.pyplot.style.use('ggplot')
    chart = fig.subplots()
    # chart = fig.figure.Figure.subplots()
    x1 = df.year
    y1 = df.annReturn
    chart.grid(True, linestyle='-')
    chart.bar(x1, y1, color="#2874A6")

    # formatting for the chart
    chart.set_xlabel('Year')
    chart.set_ylabel('Annual Return (%)')
    chart.set_title("S&P 500 Annual Returns")
    
    # annotate chart, add % and 'ytd' to last data point
    lastBar = chart.bar(x1, y1)[-1]
    lastBar.set_color("#64DD17")
    barWidth = lastBar.get_width()
    strB = f"YTD {lastBar.get_height()}%"
    chart.annotate(strB, xy=(lastBar.get_x()-3, lastBar.get_height()-5), fontsize=10)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def growthRates(df):
    fig = Figure(figsize=(10,6))
    chart = fig.subplots()
    x2 = df.index
    y2 = df['10 CAGR']
    x4 = df.index
    y4 = df['20 CAGR']
    x5 = df.index
    y5 = df['30 CAGR']
    x6 = df.index
    y6 = df['1950 CAGR']

    l = ['10 years', '20 years', '30 years', 'Current Since 1950']

    chart.plot(x2, y2, color='#85C1E9', marker='', linewidth=1.0)
    chart.plot(x4, y4, color='#2E86C1', marker='', linewidth=1.0)
    chart.plot(x5, y5, color='#1B4F72', marker='', linewidth=1.0)
    chart.plot(x6, y6, color='#E67E22', marker='', linewidth=1.0)

    # formatting for the chart
    chart.set_xlabel('Date')
    chart.grid(True, linestyle='-')
    chart.tick_params(labelcolor='black')
    chart.legend(loc='lower right', labels=l, fontsize='medium')
    chart.set_title("Current CAGR, trailing periods")
    chart.set_ylabel('CAGR (%)', color="#2E86C1")

    # annotate last datapoint with mean of plot
    strM10 = f"Avg {round(df['10 CAGR'].mean(), 2)}%"
    strM20 = f"Avg {round(df['20 CAGR'].mean(), 2)}%"
    strM30 = f"Avg {round(df['30 CAGR'].mean(), 2)}%"
    str1950 = f"{round(df['1950 CAGR'].mean(), 2)}%"

    chart.text(x2[-1], y2[-1], strM10)
    chart.text(x4[-1], y4[-1], strM20)
    chart.text(x5[-1], y5[-1], strM30)
    chart.text(x6[0], y6[0]+0.5, str1950)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    return base64.b64encode(buf.getbuffer()).decode("ascii")