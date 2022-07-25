from ast import Mult
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB,get_mean_Sentiment,get_Sentiment_Chart,show_wordCloud, get_word_insights

from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd
##PAGE SETUP
log_dir = 'streamlit_Logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_name = '{}_stream.log'.format(date.today().strftime('%Y%m%d'))
log_handler = RotatingFileHandler(filename=os.path.join(log_dir, log_name), maxBytes=2000000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                    datefmt='%d-%m-%Y T%H:%M:%S')
logger = logging.getLogger(__name__)
st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader(f"Twitter Sentiment-Streaming for {date.today().strftime('%d-%m-%Y')}")

@st.cache(ttl=60*5,allow_output_mutation=True,show_spinner=False)
def loading_data_from_heroku_database():
    df = get_Heroku_DB()
    print("Retrieved new Data from Database...")
    return df



#st.dataframe(df)
    
with st.sidebar:
    lookback_hours = st.slider("How many hours to look back?",min_value=1,max_value=24,value=4)
    group_by_min = st.select_slider("Group Timestamps by Minutes",options=[1,5,10,15,30,60],value=5)
    with st.expander("See explanation"):
        st.write("The sentiment score is a number between -1 and 1. "
            "Negative values indicates negative Sentiment."
            "Around zero is neutral Sentiment (+-0.2)."
            )


df  = loading_data_from_heroku_database()

btc_df = df[df["Keyword"].isin(["#btc","$btc","bitcoin"])]
ada_df =  df[df["Keyword"].isin(["#ada","$ada","cardano"])]
df_mean_btc_by_Minute = get_mean_Sentiment(btc_df,lookback_hours,group_by_min)
df_mean_ada_by_Minute = get_mean_Sentiment(ada_df,lookback_hours,group_by_min)
# word_cloud_btc , df_btc_word_count = get_word_insights(btc_df,lookback_hours)
# word_cloud_ada , df_ada_word_count = get_word_insights(ada_df,lookback_hours)
    # return btc_df, ada_df, df_mean_btc_by_Minute, df_mean_ada_by_Minute, word_cloud_btc,word_cloud_ada, df_btc_word_count, df_ada_word_count
    
#Get Dataframes

#st.dataframe(df_btc_word_count)


col1,col2 = st.columns(2)
with col1:
    st.subheader("Bitcoin")
    get_Sentiment_Chart(df_mean_btc_by_Minute,"btc","k")
    #show_wordCloud(word_cloud)
with col2:
    st.subheader("Cardano")
    get_Sentiment_Chart(df_mean_ada_by_Minute,"ada","c")
    #show_wordCloud(word_cloud)
    
    
