from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging
from posixpath import split
from re import S
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from words import get_signals
from streamlit_data import get_Heroku_DB,calc_mean_sent,show_charts,show_cake_diagram,resample_df, split_DF_by_time
from words import show_wordCloud,get_signal_by_keywords
from financial_data import getminutedata,getDateData,get_kucoin_data
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd

st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )

count = st_autorefresh(interval=1000*60*5, key="sent")

@st.experimental_memo(show_spinner=True,suppress_st_warning=True,ttl=5*60)
#@st.cache(ttl=60*5,allow_output_mutation=True,show_spinner=True,suppress_st_warning=True)
def loading_data_from_heroku_database():
    if lookback_timeframe > 24:
        df, df_trades, duplicates = get_Heroku_DB(today=False)
    elif lookback_timeframe <=24:
        df, df_trades, duplicates = get_Heroku_DB(today=True)
    return df,df_trades, duplicates


with st.sidebar:
    st.info("Turn on Darkmode in upper right settings!")
    hide_explanation = st.checkbox(label="Hide Explanation",value=False)
    hide_single_tweets = st.checkbox(label="Hide Tweet Metrics",value=True)
    hide_sentiment = st.checkbox(label="Hide Sentiment Metrics",value=False)
    hide_Wordcloud_and_TweetSent = st.checkbox(label="Hide Word Analysis",value=True)
    hide_Charts = st.checkbox(label="Hide Charts",value=True)
    hide_trades = st.checkbox(label="Hide Trades",value=False)
    lookback_timeframe = 96# st.select_slider("Timeframe: Last X hours",options=[1,6,12,24,72,96],value=96, help="The more days you want to look at, the longer it may take to load the database",on_change=loading_data_from_heroku_database)
    intervals = 60 #rst.select_slider("Resample Timeperiod by X Minutes",options=[1,5,15,30,60,120,360],value=60)

    


#Get Dataframes
#Convert Database to Dataframe
df, df_trades, duplicates  = loading_data_from_heroku_database()

st.subheader(f"{date.today().strftime('%d-%m-%Y')} - Bitcoin")


single_sent_scores_df,resampled_mean_tweetcount = resample_df(df, intervals, True, False)#(split_DF_by_time(df,lookback_timeframe),intervals,True)

data = getminutedata("BTCUSDT",intervals,lookback_timeframe)

if not hide_explanation:
    st.subheader("Explanation")
    st.write("This is a site to visualise a few metrics from the project")
    st.markdown("**[Social Signal Sentiment-Based Prediction for Cryptocurrency Trading](https://github.com/moerv9/sentiment)**")
    st.write("The project aims to analyse the sentiment/opinion from tweets on Twitter about Bitcoin and converts these into trading-signals.")
    st.write("The sentiment score is a number between -1 and 1. "
                "Values above 0.2 indicate a positive Sentiment and a Buy-Signal. Values below are negative and indicate a Sell-Signal.")
    st.write("Below you can have a look at different real-time metrics.")
    st.write("Click the checkboxes on the left sidebar to hide/show metrics.")
    st.markdown("---")

if not hide_single_tweets:
    st.subheader("Last collected Tweets")
    rows = st.slider("Rows to retrieve:",step=5,min_value=5,max_value=500,value=5)
    st.dataframe(df.head(rows))
    st.markdown("---")





#calculates the Mean/Average for the past time and in sums of min_range (Default 5 Minutes)
percentage_btc_df = calc_mean_sent(split_DF_by_time(df,1),False)

#Gets single words in the tweets and their frequencies + sentiment
#freq_df = get_signals(past_btc_df_for_timerange,intervals)

if not hide_sentiment:
    st.subheader("Sentiment Metrics")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.metric(label=f"Total Tweets gathered last 4 days", value=df.shape[0])
    with col2:
        st.metric(label = f"Tweets gathered last 24h", value = split_DF_by_time(df,24).shape[0])
    with col3:
        st.metric(label="Deleted Duplicates",value=duplicates)
    st.write("##")
    st.write("##")
    col1,col2 = st.columns(2)
    with col1:
        st.text("Tweet sentiment for the last hour")
        #st.dataframe(percentage_btc_df)
        show_cake_diagram(percentage_btc_df)
    with col2:
        st.text(f"Last 5 Periods with Average Sentiment and total amount of Tweets")
        st.dataframe(resampled_mean_tweetcount.head(5))
    

    st.markdown("---")
        
if not hide_Wordcloud_and_TweetSent:
    st.subheader("Word Analysis")
    words_df = get_signal_by_keywords(split_DF_by_time(df,1))
    col1,col2,col3 = st.columns(3)   
    with col1:
        st.text("Most used Words in the last hour")
        #show_wordCloud(words_df[0],False)
        show_wordCloud(split_DF_by_time(df,1),True)
    with col2:
        st.text("Most used Words that indicate buy or sell")
        st.dataframe(words_df[0])

    with col3:
        st.text("Total Count")
        st.dataframe(words_df[1])
    #st.text(f"Word Frequency in all Tweets for last {lookback_timeframe} hours ")
    #st.text(freq_df)
    # st.text("Total Signal Count")
    # st.dataframe(signals_count)
    st.markdown("---")



if not hide_Charts:
    st.subheader("Charts")
    show_charts(resampled_mean_tweetcount,data)
    st.markdown("---")


last_trade_time = df_trades["avgTime"][0]
second_last_avg = resampled_mean_tweetcount.head(2).iloc[1]
st.subheader(f"Last Trade for Timestamp: {last_trade_time}")


if not hide_trades:
    st.subheader("Trades")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.metric(label="Starting Balance", value="5000 USDT")
    with col2:
        st.metric(label = f"Current Balance", value = f"{int(get_kucoin_data()[0])} USDT")
    with col3:
        st.metric(label="Current BTC",value=f"{get_kucoin_data()[1]} ₿ = {get_kucoin_data()[2]}")
    st.subheader("Last Trades")
    st.dataframe(df_trades)


