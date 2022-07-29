import psycopg2
import os
import signal
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
import logging
from datetime import date, time, timedelta,datetime
from logging.handlers import RotatingFileHandler
import subprocess
import shlex
import psutil
from time import sleep
from streamlit_autorefresh import st_autorefresh
from dateutil import tz
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
from words import get_sent_meaning
from financial_data import getminutedata

logger = logging.getLogger(__name__)

# Config
#os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment/streamlit")
# from streamlit.config import ConfigDB
DB_URL = st.secrets["DB_URL"]

# For local setup
def get_json_data():
    """Read Tweet Data for every Coin from Json File

    Returns:
        dataframes: dict
    """
    dir = "Json/" + date.today().strftime('%d-%m-%Y')
    dataframes = {}
    if os.path.exists(dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            if os.path.isfile(file_path):
                df = pd.read_json(file_path, orient="index")
                dataframes.update({filename: df})
        return dataframes

def start_local_process(coin_selection, refresh_rate):
    command = shlex.split(
        f"python3 runner.py -k \"{coin_selection}\" -i \"{refresh_rate}\"")
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def find_pid():
    """_summary_

    Returns:
        _type_: _description_
    """
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            if "runner" in str(pinfo["cmdline"]):
                logger.info(f"Process {pinfo} running...")
                return pinfo["pid"]
            else:
                continue
        except:
            return None


def split_DF_by_time(df,time_frame):
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
    timedelt = datetime.now() - timedelta(hours=time_frame,minutes=15)
    mask = (df.index > timedelt)
    df = df.loc[mask]
    return df

def get_Heroku_DB(today=True):
    conn = psycopg2.connect(DB_URL, sslmode="require")
    if today:
        limit=60000
        query = f"select * from tweet_data where Tweet_Date > current_date order by id desc limit {limit};"
    else:
        st.info("This may take a while...")
        query = f"select * from tweet_data order by id desc limit 1000000;"
    df = pd.read_sql(query, conn)
    columns = {"body": "Tweet",
                "keyword": "Keyword",
                "tweet_date": "Timestamp",
                "location": "Location",
                "verified_user": "User verified",
                "followers": "Followers",
                "user_since": "User created",
                "sentiment": "Sentiment Score",
                "sentiment_meaning": "Null"}
    df = df.drop(columns=["sentiment_meaning"])
    df = df.rename(columns=columns)
    # Needed because the conversion to local time does not work - database is in utc timezone
    df["Timestamp"] = df["Timestamp"] + timedelta(hours=2)
    return df

def calc_mean_sent(df, min_range):
    sent_meaning_list = get_sent_meaning(df["Sentiment Score"])
    df = df.filter(items=["Sentiment Score"])
    df = df.groupby(df.index, dropna=True).mean()
    df = df.resample(f"{min_range}T").mean()
    sent_meaning_df = pd.Series(sent_meaning_list)
    sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())
    sent_appearances["Sentiment"] = sent_appearances.index
    sent_appearances.rename(columns={0:"Tweets"},inplace=True)
    sent_appearances = sent_appearances[["Sentiment","Tweets"]]
    sent_percentages = pd.Series([int((num/len(sent_meaning_df))*100) for num in sent_appearances["Tweets"]])
    sent_appearances_df = pd.concat([sent_appearances.reset_index(drop=True),sent_percentages.reset_index(drop=True)],axis=1)
    sent_appearances_df.rename(columns={0:"Percentage"},inplace=True)
    return pd.DataFrame(df), sent_appearances_df


def show_sentiment_chart(df, label, color,intervals,lookback_timeframe,symbol):
    #setup
    fig, axs = plt.subplots(2,1,sharex=True,constrained_layout=True)#figsize=(10, 4))
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.rcParams['font.size'] = '8'
    #colors
    for nn,ax in enumerate(axs):
        axs[nn].title.set_color("white")
        axs[nn].xaxis.label.set_color('white') 
        axs[nn].yaxis.label.set_color('white')
        axs[nn].tick_params(axis='x', colors='white')
        axs[nn].tick_params(axis='y', colors='white')
        axs[nn].spines["left"].set_color('white')
        axs[nn].spines["bottom"].set_color('white') 
        axs[nn].spines["top"].set_alpha(0)
        axs[nn].spines["right"].set_alpha(0)
        axs[nn].set_facecolor((0,0,0,0))
        axs[nn].xaxis.set_major_locator(locator)
        axs[nn].xaxis.set_major_formatter(formatter)
    fig.patch.set_alpha(0)
    
    #set labels
    axs[0].set_title(f"Average Sentiment for {intervals} Min. Intervals")
    axs[0].set_ylabel("Sentiment Score")
    axs[1].set_title(f"Price for {label}")
    axs[1].set_xlabel("Time")
    axs[1].set_ylabel("Price ($)")
    
    #first plot for sentiment
    # x = df.index
    # y = df["Sentiment Score"]
    
    #axs[0].scatter(x,y, label=label,color=color1,edgecolor="none")#markerfacecolor="white")
    axs[0].plot(df, label=label,color=color, markersize=5) #markerfacecolor="white")
    # for i in y.values:
    #     color1 = plt.cm.viridis(i)
    #     c = [float(i)/float(10), 0.0, float(10-i)/float(10)]
    #     axs[0].plot(x,y,color=color1)
    #second plot for price
    data = getminutedata(symbol,intervals,lookback_timeframe)
    axs[1].plot(data.index,data.Close,color=color,markersize=5)
    #plt.gcf().autofmt_xdate()
    #plt.tight_layout()
    #plt.legend()
    #plt.show()
    st.pyplot(fig)

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

