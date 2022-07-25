from ast import Mult
from datetime import date, datetime, timedelta
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB,get_mean_Sentiment,get_Sentiment_Chart,show_wordCloud

from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd
##PAGE SETUP
logger = logging.getLogger(__name__)
st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader(f"Twitter Sentiment-Streaming for {date.today().strftime('%d-%m-%Y')}")

@st.cache(ttl=60*5)
def loading_data_from_heroku_database():
    return get_Heroku_DB()
#st.dataframe(df)
if st.button("Refresh Database"):
    loading_data_from_heroku_database()
    
with st.sidebar:
    lookback_hours = st.slider("How many hours to look back?",min_value=1,max_value=24,value=4)
    group_by_min = st.select_slider("Group Timestamps by Minutes",options=[1,5,10,15,30,60],value=5)
    with st.expander("See explanation"):
        st.write("The sentiment score is a number between -1 and 1. "
            "Negative values indicates negative Sentiment."
            "Around zero is neutral Sentiment (+-0.2)."
            )

    

df = loading_data_from_heroku_database()


#Get Dataframes
btc_df = df[df["Keyword"].isin(["#btc","$btc","bitcoin"])]
ada_df = df[df["Keyword"].isin(["#ada","$ada","cardano"])]
mean_btc_by_Minute= get_mean_Sentiment(btc_df,lookback_hours,group_by_min)
mean_ada_by_Minute= get_mean_Sentiment(ada_df,lookback_hours,group_by_min)


col1,col2 = st.columns(2)
with col1:
    st.subheader("Bitcoin")
    get_Sentiment_Chart(mean_btc_by_Minute,"btc","k")
    show_wordCloud(btc_df,lookback_hours)
with col2:
    st.subheader("Cardano")
    get_Sentiment_Chart(mean_ada_by_Minute,"ada","c")
    show_wordCloud(ada_df,lookback_hours)
    
    
