import psycopg2
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import pandas as pd
import numpy as np

import os
import logging
from datetime import date, time, timedelta,datetime
from logging.handlers import RotatingFileHandler

from time import sleep
from streamlit_autorefresh import st_autorefresh
from dateutil import tz
from matplotlib.ticker import (MultipleLocator,AutoMinorLocator)
import matplotlib.dates as mdates
from words import get_sent_meaning,conv_sent_score_to_meaning
from financial_data import getminutedata,get_timestamps_for_trades,get_signal_by_sent_score
import pytz

logger = logging.getLogger(__name__)

# Config
#os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment")
from config import ConfigDB

#Uncomment for Streamlit Deployment 
#DB_URL = st.secrets["DB_URL"]
#Uncomment for local Dev
DB_URL = ConfigDB().DB_URL


def get_Heroku_DB(today=True):
    conn = psycopg2.connect(DB_URL, sslmode="require")
    if today:
        limit=60000
        logger.info("Getting data from Today")
        query = f"select * from tweet_data where Tweet_Date > current_date order by id desc limit {limit};"
    else:
        logger.info("Getting data from past Today")
        query = f"select * from tweet_data where Tweet_Date > current_date - interval '4' day order by id desc limit 1000000;"
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
    rows = df.shape[0]
    duplicates = list(df.index[df.duplicated(subset=["Tweet"],keep=False)])
    df.drop_duplicates(subset=["Tweet"],keep=False,inplace=True)

    #print(f"Deleted {len(duplicates)} duplicates from a total of {rows}")
    
    query = "select * from trade_data where id > 28 order by id desc;"
    df_trades = pd.read_sql(query, conn)

    return df.sort_index(ascending=False), df_trades, len(duplicates)

def split_DF_by_time(df,time_frame,timestamp):
    """Returns Dataframe for the past hours specified in time_frame

    Args:
        df (_type_): Dataframe to split
        time_frame (_type_): timeframe to look at

    Returns:
        DataFrame: in the given timeframe
    """
    if "Timestamp" in df.columns:
        df.index = df["Timestamp"]
    df.index = pd.to_datetime(df.index)
    if timestamp == False:
        timedelt = datetime.now() - timedelta(hours= time_frame)
    else:
        timedelt = timestamp - timedelta(hours= time_frame)
        mask = (df.index < pd.to_datetime(timestamp))
        df = df.loc[mask]
        print("Df < tmestamp")
        print(df)
    mask = (df.index > timedelt)
    df = df.loc[mask]

    return df

def calc_mean_sent(df, filter_neutral=False):
    if filter_neutral:
        df = df[df["Sentiment Score"] != 0.0]
    sent_meaning_list = get_sent_meaning(df["Sentiment Score"]) #Sentiment Values to Meaning ("Positive,Negative,etc.")
    sent_meaning_df = pd.Series(sent_meaning_list)
    sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())  
    
    sent_meaning_df = pd.Series(sent_meaning_list)
    sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())
    sent_appearances["Sentiment"] = sent_appearances.index
    sent_appearances.rename(columns={0:"Tweets"},inplace=True)
    sent_appearances = sent_appearances[["Sentiment","Tweets"]]
    sent_percentages = pd.Series([int((num/len(sent_meaning_df))*100) for num in sent_appearances["Tweets"]])
    sent_appearances_df = pd.concat([sent_appearances.reset_index(drop=True),sent_percentages.reset_index(drop=True)],axis=1)
    sent_appearances_df.rename(columns={0:"Percentage"},inplace=True)
    # print("Sent appearencs")
    # print(sent_appearances_df[sent_appearances_df["Sentiment"] == "Positive"]["Percentage"])
    # df["Positive (%)"] = sent_appearances_df[sent_appearances_df["Sentiment"] == "Positive"]["Percentage"]
    # sent_app_transposed = sent_appearances_df.transpose(copy=True)
    # print("sent transposed")
    # print(sent_app_transposed)

    return sent_appearances_df

def resample_df(df,interval, filter_neutral=False,by_day=False):
    if filter_neutral:
        df = df[df["Sentiment Score"] != 0.0]
    df_follower = df.filter(items=["Followers"])
    mean_follower = df_follower.resample("1H",label="right").mean()
        
    df = df.filter(items=["Sentiment Score"])
    if by_day:
        count_tweets = df.resample(f"D",label="right").count()
        mean_df = df.resample(f"D",label="right").mean().sort_index(ascending=False)
    elif by_day == False:
        count_tweets = df.resample(f"1H",label="right").count()#count Tweets
        mean_df = df.resample(f"{interval}T",label="right").mean().sort_index(ascending=False)
    count_tweets.rename(columns={"Sentiment Score" : "Total Tweets"},inplace=True)
    
    mean_df.rename(columns={"Sentiment Score" : "Avg"},inplace=True)
    df["Sent is"] = df["Sentiment Score"].apply(conv_sent_score_to_meaning)
    
    mean_df["Sent is"] = mean_df["Avg"].apply(conv_sent_score_to_meaning)
    resampled_mean_tweetcount = pd.concat([mean_df,count_tweets],axis="columns")
    resampled_mean_tweetcount = resampled_mean_tweetcount.dropna(subset=["Avg"])
    resampled_mean_tweetcount["Signal"] = resampled_mean_tweetcount["Avg"].apply(get_signal_by_sent_score)
    pd.set_option('max_colwidth', 400)
    
    return df.sort_index(ascending=False), resampled_mean_tweetcount.sort_index(ascending=False), mean_follower

#TODO: resamplen für zeitraum und in diesem die werte für "positive,etc" zählen
# def count_sents(df,time_range):
#     print(df)
#     total_sent_count = pd.value_counts(np.array(df["Sent is"].tolist()))
#     print(total_sent_count)
#     counts = total_sent_count.resample(f"{time_range}T").count()
#     df = pd.DataFrame(counts)
#     print(df)
#     return df


# CHARTS
def show_charts(df, data):
    #setup
    fig, axs = plt.subplots(2,1,sharex=True,constrained_layout=True)#figsize=(10, 4))
    locator = mdates.AutoDateLocator(minticks=6, maxticks=20)
    formatter = mdates.ConciseDateFormatter(locator)
    plt.rcParams['font.size'] = '8'
    #colors
    for nn,ax in enumerate(axs):
        axs[nn].title.set_color("white")
        axs[nn].xaxis.label.set_color('white') 
        axs[nn].yaxis.label.set_color('white')
        axs[nn].tick_params(axis='x', colors='white',labelrotation=30)
        axs[nn].tick_params(axis='y', colors='white')
        axs[nn].spines["left"].set_color('white')
        axs[nn].spines["bottom"].set_color('white') 
        axs[nn].spines["top"].set_alpha(0)
        axs[nn].spines["right"].set_alpha(0)
        axs[nn].set_facecolor((0,0,0,0))
        axs[nn].xaxis.set_major_locator(locator)
        axs[nn].xaxis.set_minor_locator(locator)
        axs[nn].xaxis.set_major_formatter(formatter)
    fig.patch.set_alpha(0)
    
    #set labels
    #axs[1].set_title(f"Average Sentiment for {intervals} Min. Intervals")
    axs[1].set_ylabel("Sentiment Score")
    axs[0].set_xlabel("Time")
    axs[0].set_ylabel("Price ($)")
    #axs[2].set_ylabel("Amount of Tweets")
    x1 = data.index
    y1 = data.Close    
    buy_marker, sell_marker,_,_ = get_timestamps_for_trades(df,x1)
    #first plot for btc price
    axs[0].set_title(f"Sent > 0.2 => Buy")
    axs[0].plot(x1,y1,"^",label="buy",color="g",markersize=3,markevery=buy_marker)
    axs[0].plot(x1,y1,"v",label="sell",color="r",markersize=3,markevery=sell_marker)
    axs[0].plot(x1,y1,label="BTC Price",color="w",linewidth=1,markersize=3)
    
    #third plot for sentiment
    x = df.index
    y = df["Avg"]
    axs[1].plot(x,y,linestyle=":", label="Sentiment",color="orange", markersize=2,linewidth=1)
    axs[1].axhline(y=0.2,linestyle=":",color="red",linewidth=0.5)   
    axs[0].legend()
    #plt.tight_layout()
    #axs[2].plot(x,df["Total Tweets"],linestyle=":", label="Tweets",color="yellow", markersize=2,linewidth=1)
    st.pyplot(fig)

#TODO
def visualise_timeperiods(df):
    print(df.columns)
    time_periods ,avg, total_tweets,signal = df.index,df["Avg"], df["Total Tweets"],df["Signal"]
    fig1, ax1 = plt.subplots()
    ax1.title.set_color("white")
    ax1.xaxis.label.set_color('white') 
    ax1.yaxis.label.set_color('white')
    ax1.tick_params(axis='y', colors='white',labelrotation=30)
    ax1.tick_params(axis='x', colors='white')
    ax1.spines["left"].set_color('white')
    ax1.spines["bottom"].set_color('white')
    ax1.spines["top"].set_alpha(0)
    ax1.spines["right"].set_alpha(0)
    ax1.set_facecolor((0,0,0,0))
    fig1.patch.set_alpha(0)
    
    plot1 = ax1.plot(time_periods,avg,label="Avg",color="red")
    plot2 = ax1.plot(time_periods,total_tweets,label="Total Tweets",color="cyan")
    ax1.legend()
    st.pyplot(fig1)
    
    


def show_cake_diagram(df):
    labels = [i for i in df["Sentiment"]]
    sizes = [i for i in df["Percentage"]]
    colors = ['#99ff99','#66b3ff','#ff9999','#ffcc99','#ff99cc']
    fig1, ax1 = plt.subplots()
    patches,texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',  startangle=90,colors=colors,radius=.3)#textprops=dict(color="w"),shadow=True,
    for text in texts:
        text.set_color('white')
    for autotext in autotexts:
        autotext.set_color('grey')
    #plt.rcParams['figure.facecolor'] = (0.5, 0.0, 0.0, 0.5)
    #fig1.set_facecolor(color=None)
    fig1.patch.set_alpha(0)
    ax1.axis('equal')
    ax1.set_title("Positive Tweets")
    plt.setp(autotexts, size=14, weight="bold")
    plt.tight_layout()
    #plt.show()
    st.pyplot(plt)
    
#TODO
# def show_bar_chart(df):
#     sizes = [i for i in df["Percentage"]]
#     labels = [i for i in df["Sentiment"]]
#     plt.rcParams['figure.facecolor'] = (0, 0.0, 0.0, 0)
#     fig1, ax = plt.subplots()
#     ax.bar(1,sizes[0])
#     ax.bar(1,sizes[1])
#     plt.tight_layout()
#     st.pyplot(plt)
