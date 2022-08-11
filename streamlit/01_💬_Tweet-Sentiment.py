from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from words import get_signals
from streamlit_data import get_Heroku_DB,calc_mean_sent,show_charts,split_DF_by_time,show_cake_diagram,resample_df
from words import show_wordCloud,get_signal_by_keywords
from financial_data import getminutedata,getDateData,trade
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
        df,duplicates = get_Heroku_DB(today=False)
    elif lookback_timeframe <=24:
        df,duplicates = get_Heroku_DB(today=True)
    print(f"Retrieved {df.shape[0]} new Items from Database...")
    st.session_state['duplicates'] = duplicates
    return df


 
with st.sidebar:
    st.info("Turn on Darkmode in upper right settings!")
    hide_Wordcloud_and_TweetSent = st.checkbox(label="Hide Tweet Analysis",value=True)
    hide_Charts = st.checkbox(label="Hide Charts",value=False)
    lookback_timeframe = 96# st.select_slider("Timeframe: Last X hours",options=[1,6,12,24,72,96],value=96, help="The more days you want to look at, the longer it may take to load the database",on_change=loading_data_from_heroku_database)
    intervals = 60 #rst.select_slider("Resample Timeperiod by X Minutes",options=[1,5,15,30,60,120,360],value=60)
    
    with st.expander("INFO"):
        st.write("The sentiment score is a number between -1 and 1. "
            "Negative values indicates negative Sentiment."
            "Around zero is neutral Sentiment (+-0.2)."
            )
    
if "duplicates" not in st.session_state:
    loading_data_from_heroku_database()


#Get Dataframes
#Convert Database to Dataframe
df  = loading_data_from_heroku_database()
#splits the DataFrame for each coin
st.subheader(f"{date.today().strftime('%d-%m-%Y')} - Bitcoin")
#gets dataframes for the past time specified in lookback_timeframe
# past_btc_df_for_timerange = split_DF_by_time(df,lookback_timeframe)


single_sent_scores_df,resampled_mean_tweetcount = resample_df(df,intervals,True,False)#(split_DF_by_time(df,lookback_timeframe),intervals,True)

data = getminutedata("BTCUSDT",intervals,lookback_timeframe)



#calculates the Mean/Average for the past time and in sums of min_range (Default 5 Minutes)
#mean_btc,percentage_btc_df= calc_mean_sent(past_btc_df_for_timerange,intervals)
#Gets single words in the tweets and their frequencies + sentiment
#freq_df = get_signals(past_btc_df_for_timerange,intervals)

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(resampled_mean_tweetcount)
col1,col2,col3 = st.columns(3)
with col1:
    st.metric(label=f"Total Tweets gathered last {lookback_timeframe} h", value=df.shape[0])
with col2:
    st.metric(label = f"Tweets gathered last 24h", value = split_DF_by_time(df,24).shape[0])
with col3:
    st.metric(label="Deleted Duplicates",value=st.session_state.duplicates)
col1,col2 = st.columns(2)
with col1:
    if not hide_Wordcloud_and_TweetSent:
        st.text("Sentiment of all Tweets")
        #show_cake_diagram(percentage_btc_df)
    st.text(f"Sentiment Score for Tweets in a Timeframe of {lookback_timeframe} hours")
    st.dataframe(single_sent_scores_df)
    #st.text(f"Word Frequency in all Tweets for last {lookback_timeframe} hours ")
    #st.text(freq_df)
    # st.text("Total Signal Count")
    # st.dataframe(signals_count)
with col2:
    if not hide_Wordcloud_and_TweetSent:
        st.text("Most used Words")
        #TODO: Bug
        #show_wordCloud(past_btc_df_for_timerange)
    st.text(f"Average Sentiment and Tweet Count for {intervals} Min. Periods")
    st.dataframe(resampled_mean_tweetcount)
    st.download_button(
    label="Download data as CSV",
    data= csv,
    file_name='resample_btc_df.csv',
    mime='text/csv',
)
    # st.dataframe(resampled_df)

if not hide_Charts:
    show_charts(resampled_mean_tweetcount,data)

if "last_trade_snapshot" not in st.session_state or resampled_mean_tweetcount.index[0] > st.session_state["last_trade_snapshot"] and resampled_mean_tweetcount["Total Tweets"].head(1)[0] > 100:
    st.session_state["last_trade_snapshot"] = resampled_mean_tweetcount.index[0]
    last_trade_snapshot = st.session_state["last_trade_snapshot"]
    last_trades_df = trade(resampled_mean_tweetcount.head(1)["Avg"][0])
    print(f"New trade for AVG at {last_trade_snapshot}.")
    st.subheader("Last Trades")
    st.dataframe(last_trades_df)
else:
    print("No new Avg. since last trade at:")
    print(st.session_state["last_trade_snapshot"])







