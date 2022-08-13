from time import sleep
import pandas as pd
import numpy as np
import psycopg2
import logging, os, schedule
from datetime import datetime, timedelta,timezone
from Database.Trade import Trade_Table
from Database.database import session_scope
from kucoin.client import Client as kucoinClient

os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment")
from config import ConfigDB,ConfigKucoin
kconf = ConfigKucoin()
DB_URL = ConfigDB().DB_URL
kSubClient = kucoinClient(kconf.KUCOIN_SUB_KEY, kconf.KUCOIN_SUB_SECRET,kconf.KUCOIN_SUB_PASS,sandbox=True)
kMainClient = kucoinClient(kconf.KUCOIN_KEY, kconf.KUCOIN_SECRET,kconf.KUCOIN_PASS,sandbox=True)


logger = logging.getLogger(__name__)

conn = psycopg2.connect(DB_URL, sslmode="require")

class LiveTrade():
    def __init__(self) -> None:
        print("Trade Class initialised.")
        self.schedule(1)

    def get_Heroku_DB(self, today=True):
        if today:
            limit=100000
            print("Getting data from Today")
            query = f"select * from tweet_data where Tweet_Date > current_date order by id desc limit {limit};"
        else:
            logger.info("Getting data from past Today")
            query = f"select * from tweet_data where Tweet_Date > current_date - interval '4' day limit 1000000;"
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

        count_tweets = df.resample(f"1H").count()#count Tweets
        mean_df = df.resample(f"1H").mean().sort_index(ascending=False)
        count_tweets.rename(columns={"Sentiment Score" : "Total Tweets"},inplace=True)
        mean_df.rename(columns={"Sentiment Score" : "Avg"},inplace=True)
        resampled_mean_tweetcount = pd.concat([mean_df,count_tweets],axis="columns")
        resampled_mean_tweetcount = resampled_mean_tweetcount.dropna(subset=["Avg"])
        return resampled_mean_tweetcount.sort_index(ascending = False)


    def trade(self,last_avg_df):
        accounts = kSubClient.get_accounts(account_type = "trade")
        if len(accounts) == 2:
            usdt_balance = float(accounts[0]["balance"])
            btc_balance = float(accounts[1]["balance"])
        elif len(accounts) == 1:
            usdt_balance = float(accounts[0]["balance"])
        symbol = "BTC-USDT"
        if last_avg_df["Avg"] >= 0.2 and usdt_balance > 20: #usdt_balance > 10 for subClient
            try:
                funds = round(usdt_balance*0.05,5) #0.00005
                order = kSubClient.create_market_order(symbol = symbol, side = kSubClient.SIDE_BUY, funds = funds) #usdt_balance * 0.05 for subclient
                print(f"BUY ORDER executed with {funds} at {datetime.now()}")
            except Exception as e:
                print(e.message)
        elif last_avg_df < 0.2 and btc_balance > 5 and len(accounts) != 1: 
            try:
                funds = round(btc_balance*0.25,5)
                order = kSubClient.create_market_order(symbol = symbol, side = kSubClient.SIDE_SELL, funds = funds)
                print(f"SELL ORDER executed with {funds} at {datetime.now()}")
            except Exception as e:
                print(e.message)
        sleep(10)
        orders = kSubClient.get_orders(symbol='BTC-USDT')
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
        trade = Trade_Table(pd.to_datetime(self.trade_exec_at), last_avg_df["Avg"], time, symbol, side, fundss, fee, order["orderId"], new_usdt_balance, new_btc_balance)

        with session_scope() as sess:
            sess.add(trade)
            print("Added Trade to Heroku DB")

    def trade_main(self):
        df = self.get_Heroku_DB(True)
        second_last_avg = df.head(2).iloc[1]
        query = "select * from trade_data where id > 6 order by id desc limit 1;"
        df_trades = pd.read_sql(query, conn)
        last_trade_time = df_trades["avgTime"][0]
        print(f"Check if a trade exists for {second_last_avg.name}")
        print(f"Last Trade at: {last_trade_time}")
        if second_last_avg.name > last_trade_time:#.strftime("%Y-%m-%d %H:%m:%S"):
            print(f"No Trade. Starting Trade for {second_last_avg.name}")
            self.trade(second_last_avg)
        else:
            print(f"Trade already made for {second_last_avg.name}")
            

    #Method for schedule task execution
    def schedule(self,interval = 0.5):
            schedule.every(interval).minutes.do(self.trade_main)
            while True:
                schedule.run_pending()
                sleep(1)