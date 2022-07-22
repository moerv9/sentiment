import signal
from regex import W
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os, logging
from datetime import date, time 
from logging.handlers import RotatingFileHandler
import subprocess, shlex, psutil
from time import sleep
from streamlit_autorefresh import st_autorefresh 
from collections import Counter

logger = logging.getLogger(__name__)

import os
import psycopg2
#Config
os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigDB
DB_URL = ConfigDB().DB_URL

def get_json_data():
    """Read Tweet Data for every Coin from Json File

    Returns:
        dataframes: dict
    """
    dir = "Json/"+ date.today().strftime('%d-%m-%Y')
    dataframes = {}
    if os.path.exists(dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir,filename)
            if os.path.isfile(file_path):
                df = pd.read_json(file_path,orient="index")
                dataframes.update({filename : df})
        return dataframes
    
def start_local_process(coin_selection, refresh_rate):
    command = shlex.split(f"python3 runner.py -k \"{coin_selection}\" -i \"{refresh_rate}\"")
    process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return process

def find_pid():
    """_summary_

    Returns:
        _type_: _description_
    """
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict( attrs=['pid', 'name','cmdline'])
            if "runner" in str(pinfo["cmdline"]):
                logger.info(f"Process {pinfo} running...")
                return pinfo["pid"]
            else:
                continue
        except:
            return None
        
def get_sentiment_on_all_data(sentiment_col):
    sent_avg = sentiment_col.sum() / len(sentiment_col)
    if sent_avg >0.2:
        sent_avg_eval = "Positive"
    elif sent_avg <-0.2:
        sent_avg_eval = "Negative"
    else:
        sent_avg_eval = "Neutral"
    return sent_avg, sent_avg_eval 

def show_wordCloud(df):
    try:
        all_words = ' '.join([tweets for tweets in df['Tweet']])
    except:
        print(Exception)
        pass
    word_cloud = WordCloud(width=500, height=250, random_state=21, max_font_size=100,colormap="Spectral").generate(all_words)
    plt.figure(figsize=(20,10),facecolor="k")
    plt.imshow(word_cloud, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(plt)
    #word_list = [i for item in df['Tweet'] for i in item.split()]
    #freq = Counter(word_list).most_common(10)
    
def get_Heroku_DB(limit=1000000):
    conn = psycopg2.connect(DB_URL,sslmode="require")
    cur = conn.cursor()
    query = f"select * from tweet_data order by id desc limit {limit};"
    results = pd.read_sql(query, conn)
    return results