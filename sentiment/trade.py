from time import sleep
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta,timezone
from Database.Trade import Trade_Table
from Database.database import session_scope
from kucoin.client import Client as kucoinClient

import re

os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment")
from config import ConfigDB,ConfigKucoin
kconf = ConfigKucoin()
DB_URL = ConfigDB().DB_URL
kSubClient = kucoinClient(kconf.KUCOIN_SUB_KEY, kconf.KUCOIN_SUB_SECRET,kconf.KUCOIN_SUB_PASS,sandbox=True)
kMainClient = kucoinClient(kconf.KUCOIN_KEY, kconf.KUCOIN_SECRET,kconf.KUCOIN_PASS,sandbox=True)

conn = psycopg2.connect(DB_URL, sslmode="require")


def get_Heroku_DB():
    print("Getting data from Today")
    limit=100000
    query = f"select * from tweet_data where Tweet_Date > current_date order by id desc limit {limit};"
    df = pd.read_sql(query, conn)
    columns = {"body": "Tweet",
                "keyword": "Keyword",
                "tweet_date": "Timestamp",
                "location": "Location",
                "verified_user": "User verified",
                "followers": "Followers",
                "user_since": "User created",
                "sentiment": "Sentiment Score",
                }
    #df = df.drop(columns=["sentiment_meaning"])
    df = df.rename(columns=columns)
    df.index = df["Timestamp"]
    df.drop(columns=["Timestamp"],inplace=True)
    df.index = df.index + timedelta(hours=2)
    df.index = df.index.floor("Min")
    #print(df.index.tz_localize("Europe/Berlin"))
    
    # Deleting duplicates
    rows = df.shape[0]
    duplicates = list(df.index[df.duplicated(subset=["Tweet"],keep=False)])
    df.drop_duplicates(subset=["Tweet"],keep=False,inplace=True)
    print(f"Deleted {len(duplicates)} duplicates from a total of {rows}")
    
    # Filtering neutral sentiment scores 
    df = df.filter(items=["Sentiment Score"])
    df = df[df["Sentiment Score"] != 0.0]

    count_tweets = df.resample(f"1H",label="right").count()#count Tweets
    mean_df = df.resample(f"1H",label="right").mean().sort_index(ascending=False)
    count_tweets.rename(columns={"Sentiment Score" : "Total Tweets"},inplace=True)
    mean_df.rename(columns={"Sentiment Score" : "Avg"},inplace=True)
    resampled_mean_tweetcount = pd.concat([mean_df,count_tweets],axis="columns")
    resampled_mean_tweetcount = resampled_mean_tweetcount.dropna(subset=["Avg"])
    return resampled_mean_tweetcount.sort_index(ascending = False)


def trade(last_avg_df):
    accounts = kSubClient.get_accounts(account_type = "trade")
    print(f"Starting trade process at {datetime.now()}")
    average = str(last_avg_df["Avg"])
    print("Sent Avg: {}".format(average))
    if average.startswith("-"):
        average = average[:5]
    else:
        average = average[:4]
    average = float(average)
    if len(accounts) == 2:
        if accounts[0]["currency"] == "BTC":
            btc_balance = float(accounts[0]["balance"])
            usdt_balance = float(accounts[1]["balance"])
        else:
            usdt_balance = float(accounts[0]["balance"])
            btc_balance = float(accounts[1]["balance"])
        print(f"USDT Balance: {usdt_balance} $")
        print(f"BTC Balance: {btc_balance}")
    elif len(accounts) == 1:
        if accounts[0]["currency"] == "USDT":
            usdt_balance = float(accounts[0]["balance"])
        else:
            usdt_balance = float(accounts[1]["balance"])
        print(f"USDT Balance: {usdt_balance} $")
    symbol = "BTC-USDT"
    if float(average) > 0.20: #usdt_balance > 10 for subClient
        try:
            if usdt_balance < 10:
                funds = usdt_balance
            funds = int(usdt_balance*0.05)
            print(f"Buying for {funds}")
            order = kSubClient.create_market_order(symbol = symbol, side = kSubClient.SIDE_BUY, funds = funds) #usdt_balance * 0.05 for subclient
        except Exception as e:
            print(f"Exception: {e}")
    elif float(average) <= 0.20 and len(accounts) != 1: 
        counter = 0
        while True:
            counter +=1
            if btc_balance > 0.0005:
                sellfunds = round(btc_balance * 0.25,5)
            elif btc_balance == 0.0:
                break
            else:
                sellfunds = btc_balance
            print(f"Selling for {sellfunds}")
            order = kSubClient.create_market_order(symbol = "BTC-USDT", side = kSubClient.SIDE_SELL, size = sellfunds)
            print(f"SELL ORDER executed with {sellfunds} at {datetime.now()}")
            if order:
                break
            else:
                sellfunds = btc_balance
            if counter == 5:
                print("Something went wrong. No trade executed.")
                break
    else:
        print("Trade not fulfilled.")
        print("Maybe there are not enough funds")
    sleep(10)
    orders = kSubClient.get_orders(symbol='BTC-USDT')
    if order:
        try:
            for i in orders["items"]:
                if i["id"] == str(order["orderId"]):#order["orderId"]:
                    time = pd.to_datetime(i["createdAt"],unit="ms",utc=True) + timedelta(hours=2)
                    fee =  float(i["fee"])
                    side =  i["side"]
                    fundss = float(i["funds"])
            accounts = kSubClient.get_accounts(account_type = "trade")
            new_usdt_balance = float(accounts[0]["balance"])
            new_btc_balance = float(accounts[1]["balance"])
            print(f"New Balances: {new_usdt_balance} $ and {new_btc_balance} btc.")
            trade = Trade_Table(pd.to_datetime(last_avg_df.name), last_avg_df["Avg"], time, symbol, side, fundss, fee, order["orderId"], new_usdt_balance, new_btc_balance)

            with session_scope() as sess:
                sess.add(trade)
                print("Added Trade to Heroku DB")
        except Exception as e:
            print(f"Exeption: {e}")  

def trade_main():
    try:
        df =  get_Heroku_DB()
        second_last_avg = df.head(2).iloc[1]
        query = "select * from trade_data where id > 6 order by id desc limit 1;"
        df_trades = pd.read_sql(query, conn)
        last_trade_time = df_trades["avgTime"][0]
        print(f"Check if a trade exists for {second_last_avg.name}")
        print(f"Last Trade at: {last_trade_time}")
        if second_last_avg.name > last_trade_time:#.strftime("%Y-%m-%d %H:%m:%S"):
            print(f"No Trade. Starting Trade for {second_last_avg.name}")
            trade(second_last_avg)
        else:
            print(f"Trade already made for {second_last_avg.name}")
    except Exception as e:
        print(f"Exception at {datetime.now()}: {e}")
        

trade_main()
