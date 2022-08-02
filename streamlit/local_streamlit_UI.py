import signal
from regex import W
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os, logging
from datetime import date, time 
import subprocess, shlex, psutil
from time import sleep
from streamlit_autorefresh import st_autorefresh 

from streamlit_data import show_wordCloud,sent_meaning

##PAGE SETUP
logger = logging.getLogger(__name__)
st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader(f"Twitter Sentiment-Streaming for {date.today().strftime('%d-%m-%Y')}")

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



#Wordcloud for all Coins
def show_data():
    try:
        i=0
        cols= st.columns(len(dataframes.keys()))
        for key, df in dataframes.items():
            with cols[i]:
                with st.expander(key[:-5].upper(),expanded=True):
                    sent_avg, sent_avg_eval = sent_meaning(df["Sentiment Score"])
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
                start_local_process(coin_selection,refresh_rate)
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
# st.sidebar.markdown("---")
# btn_whats_this = st.sidebar.button("What's this?")
# if btn_whats_this:
#     with st.expander("What's this?"):
#         st.write("This is a Programm that listens to the Sentiment of Tweets from Twitter and visualises it. Createdy by Moerv")
#         img_to_my_pic = '<div align="center"><a href="https://github.com/moerv9/sentiment"><img src="https://github.com/moerv9.png" alt="Github Profile" width="200"></div>'
#         st.markdown(img_to_my_pic,unsafe_allow_html=True)
        
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
        
