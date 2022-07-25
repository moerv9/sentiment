import psycopg2
import os
import signal
from regex import W
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS
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

logger = logging.getLogger(__name__)

# Config
os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment")
from config import ConfigDB
DB_URL = ConfigDB().DB_URL


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


def get_sentiment_on_all_data(sentiment_col):
    sent_avg = sentiment_col.sum() / len(sentiment_col)
    if sent_avg > 0.2:
        sent_avg_eval = "Positive"
    elif sent_avg < -0.2:
        sent_avg_eval = "Negative"
    else:
        sent_avg_eval = "Neutral"
    return sent_avg, sent_avg_eval


def show_wordCloud(df):
    all_words = ' '.join([tweets for tweets in df['Tweet']])
    my_stopwords={"amp", "cardano", "bitcoin","ada","btc"}
    my_stopwords.update(STOPWORDS) 
    word_cloud = WordCloud(max_words=50,stopwords=my_stopwords,
                        width=500, height=250,collocations=False, random_state=1, max_font_size=100, background_color="black",colormap="viridis_r").generate(all_words)
    plt.figure(figsize=(20, 10))
    plt.imshow(word_cloud, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(plt)
    print("showing wordcloud")
    
def split_DF_by_time(df,total_past_time):
    df.index = df["Timestamp"]

    df.index = pd.to_datetime(df.index)
    timedelt = datetime.now() - timedelta(hours=total_past_time)
    mask = (df.index > timedelt)
    df = df.loc[mask]
    return df

def get_word_insights(df):
    all_words = ' '.join([tweets for tweets in df['Tweet']])
    stopwords=["amp", "cardano", "bitcoin"]
    words = list(set(all_words.split(" ")))
    set_words = [i for i in words if i not in stopwords]
    #print(f"SetWords \n{set_words}")
    counts = [words.count(i) for i in set_words]
    df = pd.DataFrame(zip(set_words,counts),columns=["Words","Count"])
    df.sort_values("Count",inplace=True,ascending=False)
    df.reset_index(drop=True, inplace=True)
    print("Getting word insights...")
    return df


def get_Heroku_DB(limit=100000):
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
    print("Getting Sentiment Mean...")
    return pd.DataFrame(df)


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
    print("Showing Sentiment Chart...")
