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
client = Client(conf[0],conf[1])
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


def chart_for_coin(symbol,interval,lookback_timeframe,color,shared_x_axis):
    data = getminutedata(symbol,f"{interval}m",f"{lookback_timeframe}h")
    fig, ax = plt.subplot(212,sharex=shared_x_axis)
    plt.cla()
    #xaxis 
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    #colors
    ax.title.set_color("white")
    ax.xaxis.label.set_color('white') 
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines["left"].set_color('white')
    ax.spines["bottom"].set_color('white') 
    ax.spines["top"].set_alpha(0)
    ax.spines["right"].set_alpha(0)
    fig.patch.set_alpha(0)
    ax.set_facecolor(color="b")
    ax.patch.set_alpha(0)
    
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.set_title(asset)
    plt.tight_layout()
    ax.plot(data.index,data.Close,color=color,markersize=5)
    st.pyplot(fig)

