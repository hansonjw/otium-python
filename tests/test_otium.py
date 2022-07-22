import pytest
from otium.routes.plotCharts.chartData import indexData
from otium.routes.plotCharts.cycleData import findCycles, createCycleData
from otium.db import getCycleDates

@pytest.fixture()
def t():
    return indexData()

def test_dates(t):
    assert t._lastUpdate == t.get_today()

# def test_setNormal(t):
#     print(type(t._normData))
#     print(t._normData)
#     assert t._normData.Close[0] == 1

def test_get_rawData(t):
    assert t.get_rawData() is not None

def test_get_normData(t):
    # print(t.get_normData()[-100: ])
    assert t.get_normData() is not None

def test_get_cycle_dates(t):
    u = t.get_cycleDates()
    print(u)
    assert u is not None



# 'run inside an application' error...ugh
@pytest.mark.xfail
def test_set_cycle_data(t):
    u = t.set_cycleData()
    print(u)
    assert u is not None

# I don't quite have it straight in my mind where I want these cycle dates to exist? DB, live object, etc...
@pytest.mark.xfail
def test_getCycleDates(t):
    var = t.get_cycleData()
    assert var is not None

