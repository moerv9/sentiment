from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging, time
from posixpath import split
from re import S
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from words import get_signals
from streamlit_data import get_Heroku_DB,calc_mean_sent,show_charts,show_cake_diagram,resample_df, split_DF_by_time,visualise_timeperiods,visualise_word_signals,show_trade_chart
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
    df, df_trades, duplicates = get_Heroku_DB(today=False)
    df_trades.replace(df_trades[df_trades["id"]== 59]["usdt_balance"][0],2524.543209,inplace=True)
    df_trades.replace(df_trades[df_trades["id"]== 59]["btc_balance"][0],0.05575778,inplace=True)
    return df,df_trades, duplicates


with st.sidebar:
    st.info("Turn on Darkmode in upper right settings!")
    hide_explanation = st.checkbox(label="Hide Explanation",value=True)
    hide_most_important_metrics = st.checkbox(label="Hide most important metrics",value=True)
    hide_single_tweets = st.checkbox(label="Hide Last Collected Tweets",value=True)
    hide_sentiment = st.checkbox(label="Hide Sentiment Metrics",value=True)
    hide_Wordcloud_and_TweetSent = st.checkbox(label="Hide Word Analysis",value=True)
    hide_trades = st.checkbox(label="Hide Trades",value=False)
    intervals = 60 #rst.select_slider("Resample Timeperiod by X Minutes",options=[1,5,15,30,60,120,360],value=60)

#Get Dataframes
#Convert Database to Dataframe
df, df_trades, duplicates  = loading_data_from_heroku_database()


st.subheader(f"{date.today().strftime('%d-%m-%Y')} - Bitcoin")


single_sent_scores_df,resampled_mean_tweetcount,mean_follower = resample_df(df, intervals, True, False)#(split_DF_by_time(df,lookback_timeframe),intervals,True)

last_avail_tweets_1h = split_DF_by_time(df,1,resampled_mean_tweetcount.index[0]) # gets all the last tweets from the last available timestamp - 1h


#calculates the Mean/Average for the past time and in sums of min_range (Default 5 Minutes)
percentage_btc_df = calc_mean_sent(last_avail_tweets_1h,False)



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


if not hide_most_important_metrics:
    st.subheader("Most important Metrics")
    col1,col2 = st.columns(2)
    current_sent = resampled_mean_tweetcount["Avg"].head(1)
    current_sent_is = resampled_mean_tweetcount["Sent is"].head(1)[0]
    current_signal = resampled_mean_tweetcount["Signal"].head(1)[0]
    with col1:
        st.metric(label="Current Sentiment",value = round(current_sent,4),delta=current_sent_is,delta_color="off")
    with col2:
        st.metric(label="Current Signal",value=current_signal)
    st.markdown("---")
    



if not hide_single_tweets:
    st.subheader("Last collected Tweets")
    rows = st.slider("Rows to retrieve:",step=5,min_value=5,max_value=500,value=5)
    st.dataframe(df.head(rows))
    st.markdown("---")




#Gets single words in the tweets and their frequencies + sentiment
#freq_df = get_signals(past_btc_df_for_timerange,intervals)
if not hide_sentiment:
    st.subheader("Sentiment Metrics")
    col1,col2 = st.columns(2)
    col1.text("Last 4 days")
    col2.text("Last 24 hours")
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric(label=f"Collected Tweets", value=df.shape[0])
    with col2:
        st.metric(label="Deleted Duplicates",value=f"{int(duplicates/df.shape[0]*100)} %")

    with col3:
        st.metric(label = f"Collected Tweets", value = split_DF_by_time(df,24,False).shape[0])
    with col4:
        st.metric(label="Average Followers",value=int(mean_follower["Followers"].tail(1)))
    st.write("##")
    st.write("##")

    col1,col2 = st.columns(2)
    with col1:
        st.text("Tweet sentiment for the last hour")
        #st.dataframe(percentage_btc_df)
        show_cake_diagram(df = percentage_btc_df,which = "percentage")
    with col2:
        #TODO: als chart in most important metrics
        st.text(f"Last 5 Periods with Average Sentiment and total amount of Tweets")
        st.dataframe(resampled_mean_tweetcount.head(5))
        #visualise_timeperiods(resampled_mean_tweetcount.head(5))
    st.markdown("---")
        
if not hide_Wordcloud_and_TweetSent:
    st.subheader("Word Analysis")
    signal_by_keywords_df = get_signal_by_keywords(last_avail_tweets_1h)
    col1,col2,col3 = st.columns(3)   
    with col1:
        st.text("Most used Words in the last hour")
        #show_wordCloud(words_df[0],False)
        show_wordCloud(last_avail_tweets_1h,True)
    with col2:
        st.text("Most used Words that indicate Buy or Sell")
        #st.dataframe(signal_by_keywords_df[0])
        visualise_word_signals(signal_by_keywords_df[0])
    with col3:
        st.text("Total Proportions")
        show_cake_diagram(df = signal_by_keywords_df[1],which="signal count")
        #st.dataframe( words_df[1])
    #st.text(f"Word Frequency in all Tweets for last {lookback_timeframe} hours ")
    #st.text(freq_df)
    # st.text("Total Signal Count")
    # st.dataframe(signals_count)
    st.markdown("---")





last_trade_time = df_trades.index[0]
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
    #TODO: als chart visualisieren
    st.subheader("Last Trades")
    important_df_trades = df_trades[["side","usdt_balance","btc_balance","fee"]]
    #st.dataframe(important_df_trades)
    time_frame = 24
    #data = getminutedata("BTCUSDT",intervals,time_frame)
    #show_charts(split_DF_by_time(df_trades,time_frame,False),data)
    show_trade_chart(split_DF_by_time(df_trades,96,False))


