from ast import Mult
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB,calc_mean_sent,show_sentiment_chart,split_DF_by_time,show_cake_diagram
from words import show_wordCloud,getFrequencies_Sentiment
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd

st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )


@st.cache(ttl=60*10,allow_output_mutation=True,show_spinner=True)
def loading_data_from_heroku_database():
    df = get_Heroku_DB()
    print("Retrieved new Data from Database...")
    return df

@st.cache(allow_output_mutation=True)
def get_data():
    return df[df["Keyword"].isin(["#btc","$btc","bitcoin"])], df[df["Keyword"].isin(["#ada","$ada","cardano"])]

#st.dataframe(df)
    
with st.sidebar:
    btc_or_ada = st.radio(label="Show Coin", options=("Bitcoin","Cardano"))
    hide_Wordcloud_and_TweetSent = st.checkbox(label="Hide Tweet Analysis",value=True)
    lookback_hours = st.slider("Timeframe: Last X hours",min_value=1,max_value=24,value=4)
    intervals = st.select_slider("Group Timestamps by X Intervals",options=[1,5,10,15,30,60],value=5)
    with st.expander("See explanation"):
        st.write("The sentiment score is a number between -1 and 1. "
            "Negative values indicates negative Sentiment."
            "Around zero is neutral Sentiment (+-0.2)."
            )
st.subheader(f"{date.today().strftime('%d-%m-%Y')}: {btc_or_ada}")
#Get Dataframes
#Convert Database to Dataframe
df  = loading_data_from_heroku_database()
#splits the DataFrame for each coin
btc_df, ada_df = get_data() 

if btc_or_ada == "Bitcoin":
    #gets dataframes for the past time specified in lookback_hours (Default: last 4 hours)
    past_btc_df_for_timerange = split_DF_by_time(btc_df,lookback_hours)
    #calculates the Mean/Average for the past time and in sums of min_range (Default 5 Minutes)
    mean_btc,percentage_btc_df = calc_mean_sent(past_btc_df_for_timerange,intervals)
    #Gets single words in the tweets and their frequencies + sentiment
    _, word_freq_and_sent_btc = getFrequencies_Sentiment(past_btc_df_for_timerange)
    st.text(f"Looking at a Timeframe of {lookback_hours} hours.")
    col1,col2 = st.columns(2)
    with col1:
        st.metric(label=f"Tweets in the last {lookback_hours}h", value=split_DF_by_time(btc_df,lookback_hours).shape[0])
        if not hide_Wordcloud_and_TweetSent:
            st.text("Most used Words")
            show_wordCloud(past_btc_df_for_timerange)
    with col2:

        st.metric(label="last 24h", value=split_DF_by_time(btc_df,24).shape[0])
        if not hide_Wordcloud_and_TweetSent:
            st.text("Sentiment of all Tweets")
            show_cake_diagram(percentage_btc_df)
        
    show_sentiment_chart(mean_btc,"btc","g",intervals)
    #st.dataframe(word_freq_and_sent_btc)


elif btc_or_ada =="Cardano":
    past_ada_df_for_timerange = split_DF_by_time(ada_df,lookback_hours)
    mean_ada,percentage_ada_df = calc_mean_sent(past_ada_df_for_timerange,intervals) 
    _, word_freq_and_sent_ada = getFrequencies_Sentiment(past_ada_df_for_timerange)
    st.text(f"Looking at a Timeframe of {lookback_hours} hours.")
    col1,col2 = st.columns(2)
    with col1:
        st.metric(label=f"Tweets in the last {lookback_hours}h", value=split_DF_by_time(ada_df,lookback_hours).shape[0])
        if not hide_Wordcloud_and_TweetSent:
            st.text("Most used Words")
            show_wordCloud(past_ada_df_for_timerange)
    with col2:
        st.metric(label="last 24h", value=split_DF_by_time(ada_df,24).shape[0])
        if not hide_Wordcloud_and_TweetSent:
            st.text("Sentiment of all Tweets")
            show_cake_diagram(percentage_ada_df)
        
    show_sentiment_chart(mean_ada,"ada","c",intervals)
    #st.dataframe(word_freq_and_sent_ada)
    