from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging
import streamlit as st
from words import get_signals
from streamlit_data import get_Heroku_DB,calc_mean_sent,show_charts,split_DF_by_time,show_cake_diagram,resample_df
from words import show_wordCloud,get_signal_by_keywords
from financial_data import getminutedata,getDateData
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd

st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )


#@st.experimental_memo(show_spinner=True,suppress_st_warning=True)
#@st.cache(ttl=60*5,allow_output_mutation=True,show_spinner=True,suppress_st_warning=True)
def loading_data_from_heroku_database():
    if lookback_timeframe > 24:
        df = get_Heroku_DB(today=False)
    elif lookback_timeframe <=24:
        df = get_Heroku_DB(today=True)
    print(f"Retrieved {df.shape[0]} new Items from Database...")
    return df


    
with st.sidebar:
    hide_Wordcloud_and_TweetSent = st.checkbox(label="Hide Tweet Analysis",value=True)
    hide_Charts = st.checkbox(label="Hide Charts",value=False)
    lookback_timeframe = st.select_slider("Timeframe: Last X hours",options=[1,6,12,24,72],value=72, help="The more days you want to look at, the longer it may take to load the database",on_change=loading_data_from_heroku_database)
    intervals = st.select_slider("Resample Timeperiod by X Minutes",options=[1,5,15,30,60,120,360],value=60)
    with st.expander("See explanation"):
        st.write("The sentiment score is a number between -1 and 1. "
            "Negative values indicates negative Sentiment."
            "Around zero is neutral Sentiment (+-0.2)."
            )

#Get Dataframes
#Convert Database to Dataframe
df  = loading_data_from_heroku_database()
#splits the DataFrame for each coin
st.subheader(f"{date.today().strftime('%d-%m-%Y')} - Bitcoin")
#gets dataframes for the past time specified in lookback_timeframe
# past_btc_df_for_timerange = split_DF_by_time(df,lookback_timeframe)


single_sent_scores_df,resampled_mean_tweetcount = resample_df(split_DF_by_time(df,lookback_timeframe),intervals,True)

data = getminutedata("BTCUSDT",intervals,lookback_timeframe)

#calculates the Mean/Average for the past time and in sums of min_range (Default 5 Minutes)
#mean_btc,percentage_btc_df= calc_mean_sent(past_btc_df_for_timerange,intervals)
#Gets single words in the tweets and their frequencies + sentiment
#freq_df = get_signals(past_btc_df_for_timerange,intervals)

col1,col2 = st.columns(2)
with col1:
    st.metric(label=f"Total Tweets gathered last {lookback_timeframe} h", value=df.shape[0])
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
    st.metric(label = f"Tweets gathered last 24h", value = split_DF_by_time(df,24).shape[0])
    if not hide_Wordcloud_and_TweetSent:
        st.text("Most used Words")
        #TODO: Bug
        #show_wordCloud(past_btc_df_for_timerange)
    st.text(f"Average Sentiment and Tweet Count for {intervals} Min. Periods")
    st.dataframe(resampled_mean_tweetcount)
    # st.dataframe(resampled_df)

if not hide_Charts:

    show_charts(resampled_mean_tweetcount,data)








