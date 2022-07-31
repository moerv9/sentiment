from ast import Mult
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB,calc_mean_sent,show_sentiment_chart,split_DF_by_time,show_cake_diagram
from words import show_wordCloud,getFrequencies_Sentiment
from financial_data import chart_for_coin
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd

st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )


@st.cache(ttl=60*10,allow_output_mutation=True,show_spinner=True,suppress_st_warning=True)
def loading_data_from_heroku_database():
    if lookback_timeframe > 24:
        df = get_Heroku_DB(today=False)
    else:
        df = get_Heroku_DB(today=True)
    print("Retrieved new Data from Database...")
    return df


    
with st.sidebar:
    hide_Wordcloud_and_TweetSent = st.checkbox(label="Hide Tweet Analysis",value=True)
    lookback_timeframe = st.slider("Timeframe: Last X hours",min_value=1,max_value=24,value=4,on_change=loading_data_from_heroku_database)#,help="Max. 4 days",
    intervals = st.select_slider("Group Timestamps by X Intervals",options=[1,5,15,30,60,120],value=5)
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
#gets dataframes for the past time specified in lookback_hours (Default: last 4 hours)
past_btc_df_for_timerange = split_DF_by_time(df,lookback_timeframe)

#calculates the Mean/Average for the past time and in sums of min_range (Default 5 Minutes)
mean_btc,percentage_btc_df = calc_mean_sent(past_btc_df_for_timerange,intervals)
#Gets single words in the tweets and their frequencies + sentiment
_, word_freq_and_sent_btc = getFrequencies_Sentiment(past_btc_df_for_timerange)

col1,col2 = st.columns(2)
with col1:
    st.metric(label=f"Tweets in the last {lookback_timeframe}h", value=split_DF_by_time(df,lookback_timeframe).shape[0])
    if not hide_Wordcloud_and_TweetSent:
        st.text("Sentiment of all Tweets")
        show_cake_diagram(percentage_btc_df)
    #st.dataframe(mean_btc)
with col2:
    st.metric(label=f"Max Tweets gathered today", value=split_DF_by_time(df,24).shape[0])
    if not hide_Wordcloud_and_TweetSent:
        st.text("Most used Words")
        show_wordCloud(past_btc_df_for_timerange)
    #st.dataframe(percentage_btc_df)

ax = show_sentiment_chart(mean_btc,"btc","g",intervals,lookback_timeframe,"BTCUSDT")
#chart_for_coin("BTCUSDT",interval=intervals,lookback_timeframe=lookback_timeframe,color="g",shared_x_axis=ax)
#show_sent_and_price_data(mean_btc,"btc","g",intervals,lookback_timeframe,"BTCUSDT")

#TODO:  word_freq um die umwandlung des scores in "positive" etc erweitern.
#st.dataframe(word_freq_and_sent_btc)



