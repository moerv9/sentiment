'''
financial_data.py
Functions to get the data from Kucoin, get prices from Binance and for building Signals.
'''
from datetime import datetime, timedelta
from binance import Client as bClient
from kucoin.client import Client as kucoinClient
from binance.enums import *
import requests
import pandas as pd
import numpy as np
import re
import streamlit as st

#Config
# import sys
# sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigBinance, ConfigKucoin

kconf = ConfigKucoin()
bconf = ConfigBinance()
# BINANCE_API_KEY = st.secrets["BINANCE_API_KEY"] 
# BINANCE_API_SECRET = st.secrets["BINANCE_API_SECRET"] 
# KUCOIN_SUB_KEY = st.secrets["KUCOIN_SUB_KEY"]
# KUCOIN_SUB_SECRET = st.secrets["KUCOIN_SUB_SECRET"]
# KUCOIN_SUB_PASS = st.secrets["KUCOIN_SUB_PASS"]
BINANCE_API_KEY = bconf.BINANCE_API_KEY
BINANCE_API_SECRET = bconf.BINANCE_API_SECRET
KUCOIN_SUB_KEY = kconf.KUCOIN_SUB_KEY
KUCOIN_SUB_SECRET = kconf.KUCOIN_SUB_SECRET
KUCOIN_SUB_PASS = kconf.KUCOIN_SUB_PASS
#Init Binance Client
binance_client = bClient(BINANCE_API_KEY, BINANCE_API_SECRET)
kSubClient = kucoinClient(KUCOIN_SUB_KEY, KUCOIN_SUB_SECRET, KUCOIN_SUB_PASS,sandbox=True)
#kMainClient = kucoinClient(kconf.KUCOIN_KEY, kconf.KUCOIN_SECRET,kconf.KUCOIN_PASS,sandbox=True)

def get_current_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url)
    data = data.json()
    return float(data["price"])

def get_kucoin_data():
    """Get account balances, price for btc

    Returns:
        usdt_balance: Account Balance in USDT
        btc_balance: Account Balance in BTC
        kucoin_btc_in_usdt: Get Kucoin Sandbox Price for BTC 
        sandbox_btc_in_usdt: Convert BTC account Balance to USDT
        real_btc_in_usdt : Convert btc account balance to real-time btc price
        current_btc_price: Get current Btc Price
    """
    accounts = kSubClient.get_accounts(account_type = "trade")
    if accounts[0]["currency"] == "BTC":
        btc_balance = float(accounts[0]["balance"])
        usdt_balance = float(accounts[1]["balance"])
    else:
        usdt_balance = float(accounts[0]["balance"])
        btc_balance = float(accounts[1]["balance"])
    #print(f"USDT: {usdt_balance}, BTC: {btc_balance}")
    kucoin_btc_in_usdt= float(kSubClient.get_fiat_prices(symbol="BTC",base="USD").get("BTC"))
    current_btc = get_current_btc_price()

    real_btc_in_usdt = float(btc_balance) * float(current_btc)
    sandbox_btc_in_usdt = float(btc_balance) * float(kucoin_btc_in_usdt)
    
    return usdt_balance, btc_balance, round(kucoin_btc_in_usdt,2),round(sandbox_btc_in_usdt,2), round(real_btc_in_usdt,2), round(current_btc,2)


def getminutedata(symbol,interval, lookback):
    """Get Historical Price Data from Binance

    Args:
        symbol (String): "BTC-USDT"
        interval (int): interval to group the timeframes
        lookback (int): total past timeframe

    Returns:
        _type_: _description_
    """
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
    """Get Binance Data for defined days

    Args:
        symbol (String): "BTC-USDT"
        interval (int): interval to group the timeframes
        start_str (String): Start Date
        end_str (String): End Date

    Returns:
        frame: DataFrame
    """
    frame = pd.DataFrame(binance_client.get_historical_klines(symbol,interval,start_str,end_str))
    frame = frame.iloc[:,:6]
    frame.columns= ["Time","Open","High","Low","Close","Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit="ms")
    frame.index = frame.index + timedelta(hours=2) #utc to local
    #frame.index = frame.index.strftime( "%d-%m-%Y  %H:%M")  
    frame = frame.astype(float)
    return frame

#Test functions
#df = getminutedata(asset, "1m","120m")
#df = getminutedata(asset,"1m","12 July, 2022 16:00:00")
#df = getDateData(asset,"1m","12 July, 2022 20:00:00","12 July,2022 22:00:00")

def get_kucoin_klines():
    start_time = pd.Timestamp('2022-08-16 12:00:00').timestamp()
    end_time = pd.Timestamp(datetime.now().strftime("%d %B, %Y")).timestamp()
    klines = kSubClient.get_kline_data(symbol="BTC-USDT",kline_type="1hour",start=int(start_time),end=int(end_time))
    frame = pd.DataFrame(klines)
    frame = frame.iloc[:,:7]
    frame.columns= ["Time","Open","Close","High","Low","Trans. Volume","Trans. Amount"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index,unit="s")
    frame.index = frame.index + timedelta(hours=2) #utc to local
    frame = frame.astype(float)
    return frame

def get_buy_or_sell_signal(word):
    if word in ["buy","up","bullish","bought","high","pump","growth","uptrend","revolution","hold","love","trust","bull","#pump","success","hodl","like","profit","gain","long"]:
        return "BUY"
    elif word in ["sell","down","bearish","sold","never","bad","low","dump","decline","downfall","downtrend","decay","recession","short","hate","#short","#dump","loss","lost","lose"]:
        return "SELL"

def get_signal_by_sent_score(score):
    if score > 0.2:
        return "BUY"
    if score <= 0.2:
        return "SELL"
    

def get_signal_by_keywords(df):
    """Analyse all Tweets for Keywords and return Words, Count, Signal

    Args:
        df (DataFrame): Input Dataframe with Column "Tweet"

    Returns:
        df (DataFrame): Columns: Words,Count,Signal
        signal_count_df (DataFrame): Columns: Signal, Count
    """
    all_words = ' '.join([tweets for tweets in df["Tweet"]])
    words = list(all_words.split(" "))
    cleaned_words = [x for x in words if not bool(re.search('\d|_|\$|\amp|\/', x))]
    cleaned_words = [re.sub(r"\.|\!|\,|\(|\)|\-|\?|\;|\\","",x) for x in cleaned_words]
    cleaned_words = [x for x in cleaned_words if not bool(re.search("you|my|your|if|me|so|do|us|see|im|a|the|an|the|to|in|for|of|or|by|with|is|on|that|be|it|he", x))]
    cleaned_words = [x for x in cleaned_words if not len(x)==1]
    
    wordcount = pd.value_counts(np.array(cleaned_words))
    df = pd.DataFrame(wordcount,columns=["Count"])
    df["Words"] = df.index
    df = df[["Words","Count"]]
    df.reset_index(drop=True, inplace=True)
    df["Signal"] = df["Words"].apply(get_buy_or_sell_signal)
    df = df.dropna(subset=["Signal"])
    signal_count_df = df.groupby(by=["Signal"],as_index=False,sort=False).agg({"Count":"sum"})
    
    #sent_list = [sentiment_model.polarity_scores(words).get("compound") for words in df["Words"]] #Sent for each word
    #df["Sentiment"] = get_sent_meaning(sent_list)
    #df_count = df.groupby(df["Sentiment"], dropna=True).count() #count words for each sentiment "pos, neg, ..."
    return df.sort_values(by=["Count","Signal"],ascending=False), signal_count_df


def calc_pnl(df):
    trade_timeperiods = df.filter(items=["funds","side","fee","usdt_balance","btc_balance"]) 
    temp_df_time = trade_timeperiods.index
    # Binance
    data = getDateData("BTCUSDT","1h","16 Aug, 2022",datetime.now().strftime("%d %b, %Y"))
    di = data.index
    dc = data.Close
    lst = []
    for i in range(len(di)):
        if di.values[i] in trade_timeperiods.index:
            lst.append(dc.values[i])
    # Kucoin
    kdata = get_kucoin_klines()
    ki = kdata.index
    kc = kdata.Close
    klst = []
    for i in range(len(ki)):
        if ki.values[i] in trade_timeperiods.index:
            klst.append(kc.values[i])

    prices = pd.Series(lst)
    kprices = pd.Series(klst)
    temp_df = pd.concat([trade_timeperiods.reset_index(drop=True),prices.reset_index(drop=True)],axis=1)
    temp_df.rename(columns={0:"binance btc price"},inplace=True)
    
    temp_df = pd.concat([temp_df.reset_index(drop=True),kprices.reset_index(drop=True)],axis=1)
    temp_df.rename(columns={0:"kucoin btc price"},inplace=True)
    temp_df.index = temp_df_time
    #temp_df["fee_usdt"] = temp_df["fee"].apply(lambda x: x * temp_df["btc/usdt"] )
    temp_df = temp_df.assign(binance_btc_usdt=lambda x: (x['binance btc price'] * x['btc_balance']))
    temp_df = temp_df.assign(kucoin_btc_usdt=lambda x : (x["btc_balance"] * x["kucoin btc price"]))
    
    temp_df = temp_df.assign(acc_binance_balance=lambda x: (x["binance_btc_usdt"] + x["usdt_balance"] ))
    temp_df = temp_df.assign(acc_kucoin_balance = lambda x: (x["kucoin_btc_usdt"] + x["usdt_balance"] ))
    
    temp_df = temp_df.assign(pnl= lambda x :  5000 - x.acc_binance_balance)
    temp_df = temp_df.assign(kucoin_pnl= lambda x :  5000 - x.acc_kucoin_balance)
    # temp_df = temp_df[["side","fee","usdt_balance","binance btc price","binance_btc_usdt","total","pnl","kucoin btc price","kucoin_btc_usdt","kucoin_total","kucoin_pnl"]]
    temp_df = temp_df[["side","fee","usdt_balance","btc_balance","binance btc price","acc_binance_balance","kucoin btc price","acc_kucoin_balance"]]
    return temp_df
    