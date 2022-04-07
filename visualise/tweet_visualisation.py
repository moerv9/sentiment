# Imports
import streamlit as st
import pandas as pd
import numpy as np
import sys
sys.path.append("../")
import tweets as tw

# Page Settings
st.set_page_config(
    layout="wide", 
    page_title="Tweet Visualisation", 
    initial_sidebar_state="expanded",
    )
st.title("Tweet Visualisation")

# Sidebar
with st.sidebar:
    with st.form(key="input_values"):
        tweet_kind = st.radio("Type of Data",("History","Realtime"))
        if tweet_kind == "History":
            tweet_search = st.selectbox("search...",["7 days","30 days", "Full Archive"])
        else:
            pass
        #st.markdown("""---""")
        amount_tweets = st.slider("Amount of Tweets to return", min_value=1,max_value=500)
        keywords = st.text_input("Keywords", placeholder="Seperate by comma").split(",")
        submit_button = st.form_submit_button(label='Get Data')

# Functions
@st.cache
def getTweetHistory(amount_tweets) ->list:  
    historical_tweets = tw.SearchTwitterHistory().filter_by_keywords("search_tweets","mixed",keywords,amount_tweets)
    list = tw.ListToDF(historical_tweets)
    return list

def getTweetStream(amount_tweets)->list:
    stream_tweets = tw.SearchStream().filter_by_keywords([keywords])
    list = tw.ListToDF(stream_tweets)
    return list
    
# main
if submit_button:
    if tweet_kind == "History":
        resultDF = getTweetHistory(amount_tweets)
    elif tweet_kind == "Realtime":
        pass
        #resultDF = getTweetStream(amount_tweets)
    st.dataframe(resultDF.df, width=1800, height=600)