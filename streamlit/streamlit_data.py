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
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from words import get_sent_meaning

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


def split_DF_by_time(df,total_past_time):
    if "Timestamp" in df.columns:
        df.index = df["Timestamp"]
    df.index = pd.to_datetime(df.index)
    timedelt = datetime.now() - timedelta(hours=total_past_time,minutes=15)
    mask = (df.index > timedelt)
    df = df.loc[mask]
    return df

def get_Heroku_DB(limit=200000):
    conn = psycopg2.connect(DB_URL, sslmode="require")
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
                "sentiment_meaning": "Null"}
    df = df.drop(columns=["sentiment_meaning"])
    df = df.rename(columns=columns)
    # Needed because the conversion to local time does not work - database is in utc timezone
    df["Timestamp"] = df["Timestamp"] + timedelta(hours=2)
    return df

def calc_mean_sent(df, min_range):
    df = df.filter(items=["Sentiment Score"])
    df = df.groupby(df.index, dropna=True).mean()
    df = df.resample(f"{min_range}T").mean()
    sent_meaning_list = get_sent_meaning(df["Sentiment Score"])
    sent_meaning_df = pd.Series(sent_meaning_list)
    sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())
    sent_appearances["Sentiment"] = sent_appearances.index
    sent_appearances.rename(columns={0:"Tweets"},inplace=True)
    sent_appearances = sent_appearances[["Sentiment","Tweets"]]
    sent_percentages = pd.Series([int((num/len(sent_meaning_df))*100) for num in sent_appearances["Tweets"]])
    sent_appearances_df = pd.concat([sent_appearances.reset_index(drop=True),sent_percentages.reset_index(drop=True)],axis=1)
    sent_appearances_df.rename(columns={0:"Percentage"},inplace=True)
    return pd.DataFrame(df), sent_appearances_df


def show_sentiment_chart(df, label, color):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title(label)
    ax.set_xlabel("Time")
    ax.set_ylabel("Sentiment Score")
    # ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.set_xlim(auto=True)
    # ax.set_ylim(-1,1)
    ax.plot(df, label=label, color=color, marker=".", markersize=4)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    #plt.legend()
    st.pyplot(fig)

def show_cake_diagram(df):
    labels = [i for i in df["Sentiment"]]
    sizes = [i for i in df["Percentage"]]
    colors = ['#99ff99','#66b3ff','#ff9999','#ffcc99','#ff99cc']
    fig1, ax1 = plt.subplots()
    plt.rcParams['figure.facecolor'] = (0, 0.0, 0.0, 0)
    patches,texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90,colors=colors,radius=.5)#textprops=dict(color="w"))
    for text in texts:
        text.set_color('white')
    for autotext in autotexts:
        autotext.set_color('grey')
    ax1.axis('equal')
    ax1.set_title("")
    plt.setp(autotexts, size=14, weight="bold")
    plt.tight_layout()
    #plt.show()
    st.pyplot(plt)