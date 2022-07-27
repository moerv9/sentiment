import re
import multidict
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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

# Config
# os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment")
# from streamlit.config import ConfigDB
DB_URL = st.secrets["DB_URL"]
my_stopwords={"amp"}
sentiment_model = SentimentIntensityAnalyzer()

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


def get_sent_meaning(sent_list):
    sent_meaning_list = []
    for num in sent_list:
        sent_meaning_list.append(conv_sent_score_to_meaning(num))
    mean_avg = sum(sent_list) / len(sent_list)
    return mean_avg, sent_meaning_list

def conv_sent_score_to_meaning(num):
    if num > 0.2 and num < 0.6:
        return("Positive")
    elif num > 0.6:
        return("Very Positive")
    elif num < - 0.2 and num > -0.6:
        return("Negative")
    elif num < - 0.6 :
        return("Very Negative")
    else:
        return("Neutral")

def getFrequencyDictForText(df):
    all_words = ' '.join([tweets for tweets in df['Tweet']])
    words = list(set(all_words.split(" ")))
    #set_words = [i for i in words if i not in my_stopwords] #if not bool(re.search('\d|_|\$', i)
    cleaned_words = [x for x in words if not bool(re.search('\d|_|\$|\amp', x))]
    cleaned_words = [re.sub(r"\.|\!|\,|\(|\)|\-|\?|\;|\\|\'","",x) for x in cleaned_words]
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}
    # making dict for counting frequencies
    for text in cleaned_words:
        if re.match("a|the|an|the|to|in|for|of|or|by|with|is|on|that|be", text):
            continue
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    for key in tmpDict:
        fullTermsDict.add(key, tmpDict[key])
    del fullTermsDict[""]
    df = pd.DataFrame.from_dict(fullTermsDict,orient="index",columns=["Count"])
    sent_list = [sentiment_model.polarity_scores(words).get("compound") for words in df.index]
    mean_avg,sent_meaning_list = get_sent_meaning(sent_list)
    df["Sentiment"] = sent_meaning_list
    df = df.sort_values(by=["Count","Sentiment"],ascending=False)
    return df

def show_wordCloud(df):
    freq_words = getFrequencyDictForText(df)
    words = WordCloud(relative_scaling=0.5,max_words=50,stopwords=my_stopwords,
                        width=500, height=250,collocations=False, random_state=1, max_font_size=100, background_color="black",colormap="viridis_r").generate_from_frequencies(freq_words)
    plt.figure(figsize=(20, 10))
    plt.imshow(words, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(plt)
    
def split_DF_by_time(df,total_past_time):
    df.index = df["Timestamp"]
    df.index = pd.to_datetime(df.index)
    timedelt = datetime.now() - timedelta(hours=total_past_time)
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
