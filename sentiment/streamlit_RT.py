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

##PAGE SETUP
logger = logging.getLogger(__name__)
st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader(f"Twitter Sentiment-Streaming for {date.today().strftime('%d-%m-%Y')}")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style",unsafe_allow_html=True)

## FUNCTIONS
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
    word_list = [i for item in df['Tweet'] for i in item.split()]
    freq = Counter(word_list).most_common(10)
    print(freq)


def get_json_data():
    dir = "Json/"+ date.today().strftime('%d-%m-%Y')
    dataframes = {}
    if os.path.exists(dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir,filename)
            if os.path.isfile(file_path):
                df = pd.read_json(file_path,orient="index")
                dataframes.update({filename : df})
        return dataframes
    
def get_sentiment_on_all_data(sentiment_col):
    sent_avg = sentiment_col.sum() / len(sentiment_col)
    if sent_avg >0.2:
        sent_avg_eval = "Positive"
    elif sent_avg <-0.2:
        sent_avg_eval = "Negative"
    else:
        sent_avg_eval = "Neutral"
    return sent_avg, sent_avg_eval 

# @st.cache()
# def set_process_id(id=5):
#     process_id = id
#     st.session_state.process_id = process_id
#     logger.info(f"process id: {process_id}")
#     return process_id
# process_id = set_process_id()

def find_pid():
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
        
def show_data():
    try:
        i=0
        cols= st.columns(len(dataframes.keys()))
        for key, df in dataframes.items():
            with cols[i]:
                with st.expander(key[:-5].upper(),expanded=True):
                    sent_avg, sent_avg_eval = get_sentiment_on_all_data(df["Sentiment Score"])
                    st.metric("Sentiment is:",sent_avg_eval, f"{sent_avg:5f}")
                    show_wordCloud(df)
            i+=1
    except:
        logger.info(f"No Data for {date.today().strftime('%d-%m-%Y')}")
        st.write(f"No Data for {date.today().strftime('%d-%m-%Y')}")

#Sidebar
st.sidebar.subheader("Mission Control")
coin_selection = st.sidebar.multiselect("What Coins do you want to listen to?",["btc","eth","ada","bnb","xrp"],default="btc")
refresh_rate = st.sidebar.number_input("Refresh Interval",min_value=0.5,max_value=120.0,value=0.5,step=0.5,help="This refreshes the Page and reads the Data in given Interval.\nValue in Min.",format="%f") #the page should also be refreshed in that rate

#Starting & Stopping the Process
process_status_text = f'<h3 style="color:Orange;">OFFLINE</h3>'
if find_pid() is not None:
    process_status_text = f'<h3 style="color:Green;">RUNNING</h3>'
    btn_stop_runner = st.sidebar.button("Stop Listening")
    if btn_stop_runner:
        pid = find_pid()
        print(f"Killed Process with PID:{find_pid()}")
        subprocess.os.kill(pid,signal.SIGTERM)
else:
    btn_start_runner = st.sidebar.button("Start Listening")
    if btn_start_runner:
        
        with st.spinner('Wait for it...'):
            try:
                command = shlex.split(f"python3 runner.py -k \"{coin_selection}\" -i \"{refresh_rate}\"")
                process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #process_id = set_process_id(process.pid)
            except:
                Exception("Error")
            sleep(3)
        st.sidebar.success('Listening to Tweets now..!') 
        st.sidebar.warning("The page will refresh in 30 seconds. Please wait")


#Show the actual Status of the Process in Sidebar
st.sidebar.markdown(process_status_text,unsafe_allow_html=True)

page_refresh_rate=st_autorefresh(interval= refresh_rate*60*1000, key="page_refresh_rate")

## Call functions
dataframes = get_json_data()
find_pid()
show_data()

#A Button for Explanation
st.sidebar.markdown("---")
btn_whats_this = st.sidebar.button("What's this?")
if btn_whats_this:
    with st.expander("What's this?"):
        st.write("This is a Programm that listens to the Sentiment of Tweets from Twitter and visualises it. Createdy by Moerv")
        img_to_my_pic = '<div align="center"><a href="https://github.com/moerv9/sentiment"><img src="https://github.com/moerv9.png" alt="Github Profile" width="200"></div>'
        st.markdown(img_to_my_pic,unsafe_allow_html=True)
        
## Show the Tables of Data for each Coin             
btn_show_datasets = st.sidebar.button("Show Datasets")
if btn_show_datasets:
    try:
        st.markdown("---")
        st.subheader("Datasets")
        for key, df in dataframes.items():
            with st.expander(f"Tweet Data for {key[:-5].upper()}"):
                st.dataframe(df.tail(5))
    except:
        Exception("Can't display data for right now")
        


## BACKUP FOR EXCEL DATA
# #get excel and sheet names, sheet name = sentiment average
# tabs:list = pd.ExcelFile("26-04-2022_stream.xlsx").sheet_names
# slider_value = st.slider("Choose Sheet",min_value= 1,max_value=len(tabs))
# dict_df = pd.read_excel("26-04-2022_stream.xlsx",sheet_name=None)
# sent_avg = float(tabs[slider_value-1])

# df = pd.DataFrame(dict_df[tabs[slider_value-1]])
# time_col = df["Time"].values
# time = st.text(f"Duration: '{time_col[0]}'  ->  '{time_col[-1]}'")
# st.dataframe(df.head(5))
# df.style.hide(level = 1)  
# st.markdown("---")

## BACKUP FOR SQL 
# if st.slider:
#     st.text(f"Rows: {len(df)}")
#     st.subheader = "Metrics"
#     st.metric("Sentiment is",sent_avg_eval,f"{sent_avg:5f}")
#     #st.line_chart(tabs)
#     wordCloud(df)

# @st.cache(allow_output_mutation=True, show_spinner=False)
# def get_con():
#     return create_engine('postgresql://{}:{}@{}/tweets'.format(ConfigDB.USER, ConfigDB.PASS, ConfigDB.HOST),convert_unicode=True)

# @st.cache(allow_output_mutation=True,show_spinner=False, ttl=5*60)
# def get_data():
#     timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#     df = pd.read_sql_table("tweets",get_con())
#     df = df.rename(columns={"body": "Tweet", "tweet_date":"Timestamp", 
#         "followers": "Followers", "sentiment": "Sentiment", "keyword": "Keyword",
#         "verified_user": "User verified"})
#     return df, timestamp