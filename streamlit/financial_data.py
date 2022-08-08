from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from binance import Client
import pandas as pd
import os
import streamlit as st
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates

#Config
import sys
#sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigBinance
conf = ConfigBinance().getKeys(True)

#Init Binance Client
client = Client(conf[0],conf[1],testnet=True)
asset = "BTCUSDT"


def getminutedata(symbol,interval, lookback):
    if interval == 60:
        interval = "1h"
    elif interval == 120:
        interval = "2h"
    elif interval == 360:
        interval = "6h"
    else:
        interval = f"{interval}m"
    if lookback == 24:
        lookback = "1d"
    elif lookback == 72:
        lookback = "3d"
    elif lookback == 168:
        lookback = "1w"
    else:
        lookback = f"{lookback}h"
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback))
    frame = frame.iloc[:,:6]
    frame.columns= ["Time","Open","High","Low","Close","Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit="ms")
    frame.index = frame.index + timedelta(hours=2) #utc to local
    frame = frame.astype(float)
    return frame

def getDateData(symbol,interval, start_str, end_str):
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,start_str,end_str))
    frame = frame.iloc[:,:6]
    frame.columns= ["Time","Open","High","Low","Close","Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit="ms")
    #frame.index = frame.index.strftime( "%d-%m-%Y  %H:%M")  
    frame = frame.astype(float)
    return frame

#Test functions
#df = getminutedata(asset, "1m","120m")
#df = getminutedata(asset,"1m","12 July, 2022 16:00:00")
#df = getDateData(asset,"1m","12 July, 2022 20:00:00","12 July,2022 22:00:00")

def get_buy_or_sell_signal(word):
    if word in ["buy","up","bullish","bought","high","pump","growth","uptrend","revolution","hold","love","trust","bull","#pump","success","hodl"]:
        return "BUY"
    elif word in ["sell","down","bearish","sold","never","bad","low","dump","decline","downfall","downtrend","decay","recession","regess","short","hate","#short","#dump","loss","lost","lose"]:
        return "SELL"

def get_signal_by_sent_score(score):
    if score >= 0.2:
        return "BUY"
    if score < 0.2:
        return "SELL"
    
sell_vals = []
buy_vals = []
plot_buy_marker  = []
plot_sell_marker  = []
time_buy = []
time_sell = []

def get_timestamps_for_trades(avg_count_df,x1):
    avg_count_df.sort_index(ascending=False)
    for i in range(len(avg_count_df)):
        if avg_count_df["Avg"].values[i] >= 0.2:
            buy_vals.append(avg_count_df.index[i])
        else:
            sell_vals.append(avg_count_df.index[i])
    for i in range(len(x1)):
        if x1.values[i] in buy_vals:
            time_buy.append(x1.values[i])
            plot_buy_marker.append(i)
        elif x1.values[i] in sell_vals:
            plot_sell_marker.append(i)
            time_sell.append(x1.values[i])
    return plot_buy_marker, plot_sell_marker,time_buy,time_sell
