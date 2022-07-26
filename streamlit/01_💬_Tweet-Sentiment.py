from ast import Mult
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB,calc_mean_sent,show_sentiment_chart,show_wordCloud, get_word_insights,split_DF_by_time

from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd

st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader(f"{date.today().strftime('%d-%m-%Y')}")

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
    lookback_hours = st.slider("How many hours to look back?",min_value=1,max_value=24,value=4)
    min_range = st.select_slider("Group Timestamps by Minutes",options=[1,5,10,15,30,60],value=5)
    with st.expander("See explanation"):
        st.write("The sentiment score is a number between -1 and 1. "
            "Negative values indicates negative Sentiment."
            "Around zero is neutral Sentiment (+-0.2)."
            )


df  = loading_data_from_heroku_database()
btc_df, ada_df = get_data()
past_h_btc_df = split_DF_by_time(btc_df,lookback_hours)
past_h_ada_df = split_DF_by_time(ada_df,lookback_hours)

mean_btc = calc_mean_sent(past_h_btc_df,min_range) #Gets the average/mean sentiment for timesranges by [min_range] 
mean_ada = calc_mean_sent(past_h_ada_df,min_range) 
# df_btc_word_count = get_word_insights(btc_df,lookback_hours)
# df_ada_word_count = get_word_insights(ada_df,lookback_hours)
    # return btc_df, ada_df, df_mean_btc_by_Minute, df_mean_ada_by_Minute, word_cloud_btc,word_cloud_ada, df_btc_word_count, df_ada_word_count
#Get Dataframes

#st.dataframe(df_btc_word_count)
col1,col2 = st.columns(2)
with col1:
    st.subheader("Bitcoin")
with col2:
    st.subheader("Cardano")

col1,col2,col3,col4 = st.columns(4)
with col1:
    st.metric(label="Tweets in the last 24h", value=split_DF_by_time(btc_df,24).shape[0])
with col2:
    st.metric(label="last 1h", value=split_DF_by_time(btc_df,1).shape[0])
with col3:
    st.metric(label="Tweets in the last 24h", value=split_DF_by_time(ada_df,24).shape[0])
with col4:
    st.metric(label="last 1h", value=split_DF_by_time(ada_df,1).shape[0])
    

col1,col2 = st.columns(2)
with col1:
    show_sentiment_chart(mean_btc,"btc","k")
    show_wordCloud(past_h_btc_df)
    st.dataframe(get_word_insights(past_h_btc_df))
with col2:

    show_sentiment_chart(mean_ada,"ada","c")
    show_wordCloud(past_h_ada_df)
    
    
