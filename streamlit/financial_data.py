from datetime import timedelta,datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from binance import Client as bClient
from kucoin.client import Client as kucoinClient
from binance.enums import *

import pandas as pd
import os
import streamlit as st
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates

#Config
import sys
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigBinance,ConfigKucoin

kconf = ConfigKucoin()
#Init Binance Client
binance_client = bClient(ConfigBinance().BINANCE_API_KEY,ConfigBinance().BINANCE_API_SECRET)
kSubClient = kucoinClient(kconf.KUCOIN_SUB_KEY, kconf.KUCOIN_SUB_SECRET,kconf.KUCOIN_SUB_PASS,sandbox=True)
kMainClient = kucoinClient(kconf.KUCOIN_KEY, kconf.KUCOIN_SECRET,kconf.KUCOIN_PASS,sandbox=True)

def get_kucoin_data():
    accounts = kSubClient.get_accounts(account_type = "trade")
    usdt_balance = float(accounts[0]["balance"])
    btc_balance = float(accounts[1]["balance"])
    btc_price = binance_client.get_symbol_ticker(symbol="BTCUSDT")["price"]
    btc_in_usdt = float(btc_balance) * float(btc_price)
    return usdt_balance, btc_balance, btc_in_usdt


def getminutedata(symbol,interval, lookback):
    if interval == 60:
        interval = "1h"
    elif interval == 120:
        interval = "2h"
    elif interval == 240:
        interval = "4h"
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
    frame = pd.DataFrame(binance_client.get_historical_klines(symbol,interval,lookback))
    frame = frame.iloc[:,:6]
    frame.columns= ["Time","Open","High","Low","Close","Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit="ms")
    frame.index = frame.index + timedelta(hours=2) #utc to local
    frame = frame.astype(float)
    return frame

def getDateData(symbol,interval, start_str, end_str):
    frame = pd.DataFrame(binance_client.get_historical_klines(symbol,interval,start_str,end_str))
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
buy_time = []
sell_time = []

def get_timestamps_for_trades(avg_count_df,btc_timestamps):
    avg_count_df.sort_index(ascending=False)
    for i in range(len(avg_count_df)):
        if avg_count_df["Avg"].values[i] >= 0.2:
            buy_vals.append(avg_count_df.index[i])#[Timestamp('2022-08-09 14:00:00'), ,...]
        else:
            sell_vals.append(avg_count_df.index[i])
    for i in range(len(btc_timestamps)):
        if btc_timestamps.values[i] in buy_vals:
            buy_time.append(pd.to_datetime(btc_timestamps.values[i],utc=True))
            plot_buy_marker.append(i) #[1, 2, 7, 8, 10, 11, 12, 13, ...]
        elif btc_timestamps.values[i] in sell_vals:
            plot_sell_marker.append(i)
            sell_time.append(pd.to_datetime(btc_timestamps.values[i],utc=True))
    #df = pd.Series(data=True,index=buy_time)
    
    #print(pd.Series(buy_time))
    #price_for_date_df = [x.strftime("%d %B, %Y %H:%M:%S") for x in buy_time] #['05 August, 2022 17:00:00', ...]
    #price_for_date_df = getDateData("BTCUSDT","1h",price_for_date_df[0],price_for_date_df[1])
    #print(price_for_date_df.to_string())
    
    return plot_buy_marker, plot_sell_marker,buy_time,sell_time

