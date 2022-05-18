import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os, logging
from datetime import date, time 
from logging.handlers import RotatingFileHandler
from runner import Runner

from time import sleep


logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Twitter Streaming", 
    layout="wide", 
    )
st.title("Dashboard for Twitter Sentiment-Streaming")

# @st.cache(allow_output_mutation=True, show_spinner=False)
# def get_con():
#     return create_engine('postgresql://{}:{}@{}/tweets'.format(ConfigDB.USER, ConfigDB.PASS, ConfigDB.HOST),convert_unicode=True)

# @st.cache(allow_output_mutation=True,show_spinner=False, ttl=5*60)
# def get_data():
#     timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#     df = pd.read_sql_table("tweets",get_con())
#     df = df.rename(columns={"body": "Tweet", "tweet_date":"Timestamp", 
#         "followers": "Followers", "sentiment": "Sentiment", "keyword": "Keyword",
#         "verified_user": "User verified"})
#     return df, timestamp

def show_wordCloud(df):
    print(len(df["Tweet"]))
    try:
        all_words = ' '.join([tweets for tweets in df['Tweet']])
    except:
        print(Exception)
        pass
    word_cloud = WordCloud(width=500, height=250, random_state=21, max_font_size=100).generate(all_words)

    plt.imshow(word_cloud, interpolation="bilinear")
    plt.axis('off')
    st.pyplot(plt)

def get_json_data():
    dir = "Json/"+ date.today().strftime('%d-%m-%Y')
    dataframes = {}
    if os.path.exists(dir):
        for filename in os.listdir(dir):
            f = os.path.join(dir,filename)
            if os.path.isfile(f):
                df = pd.read_json(f,orient="index")
                dataframes.update({filename : df})
        return dataframes

    
def get_sentiment_on_all_data(sentiment_col):
    sent_avg = sentiment_col.sum() / len(sentiment_col)
    if sent_avg >0.1:
        sent_avg_eval = "Positive"
    elif sent_avg <-0.1:
        sent_avg_eval = "Negative"
    else:
        sent_avg_eval = "Neutral"
    return sent_avg, sent_avg_eval 

dataframes = get_json_data()

with st.sidebar:
    st.subheader("Mission Control")
    coin_selection = st.multiselect("What Coins do you want to listen to?",["btc","eth","ada","bnb","xrp"],default="btc")
    btn_start_listener = st.button("Start Listener")
    
if btn_start_listener:
    with st.spinner('Wait for it...'):
        try:
            Runner(coin_selection,0.5)
        except:
            Exception("Error")
        sleep(5)
    st.success('Listening to tweets now..!') 

st.markdown("---")
st.subheader("Overall Sentiment")
st.subheader("Last Tweets:")
try:
    for key, df in dataframes.items():
        with st.expander(key[:-5]):
            st.dataframe(df.tail(5))
            col1,col2,col3 = st.columns(3)
            with col2:
                show_wordCloud(df)
            with col3:
                sent_avg, sent_avg_eval = get_sentiment_on_all_data(df["Sentiment Score"])
                st.metric("Sentiment is",sent_avg_eval, f"{sent_avg:5f}")
except:
    logger.info(f"No Data for {date.today().strftime('%d-%m-%Y')}")
    st.write(f"No Data for {date.today().strftime('%d-%m-%Y')}")





## BACKUP FOR EXCEL DATA
# #get excel and sheet names, sheet name = sentiment average
# tabs:list = pd.ExcelFile("26-04-2022_stream.xlsx").sheet_names
# slider_value = st.slider("Choose Sheet",min_value= 1,max_value=len(tabs))
# dict_df = pd.read_excel("26-04-2022_stream.xlsx",sheet_name=None)
# sent_avg = float(tabs[slider_value-1])

# df = pd.DataFrame(dict_df[tabs[slider_value-1]])
# time_col = df["Time"].values
# time = st.text(f"Duration: '{time_col[0]}'  ->  '{time_col[-1]}'")
# st.dataframe(df.head(5))
# df.style.hide(level = 1)  
# st.markdown("---")

# def add_together(tabs):
#     list = [names for names in tabs]
#     return list

# #print(add_together(tabs))
    
# if st.slider:
#     st.text(f"Rows: {len(df)}")
#     st.subheader = "Metrics"
#     st.metric("Sentiment is",sent_avg_eval,f"{sent_avg:5f}")
#     #st.line_chart(tabs)
#     wordCloud(df)
