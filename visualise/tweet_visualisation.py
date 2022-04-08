# Imports
import streamlit as st
import pandas as pd
import numpy as np
import sys
sys.path.append("../")
import tweets
import sentiment 

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
        #tweet_search = st.selectbox("search...",["search_archive","search_30_day", "search_full_archive"],help="7 days, 30 days, Full Archive")
        #st.markdown("""---""")
        amount_tweets = st.slider("Amount of Tweets to return", min_value=1,max_value=100)
        keywords = st.text_input("Keywords", placeholder="Seperate by comma").split(",")
        submit_button = st.form_submit_button(label='Get Data')
        

# Functions
@st.cache
def getTweetHistory(amount_tweets) -> pd.DataFrame:  
    historical_tweets = tweets.SearchTwitterHistory().filter_by_keywords("search_tweets","mixed",keywords,amount_tweets)
    tm = tweets.TweetManipulation()
    df = tm.listToDataFrame(historical_tweets)
    #cleanedDF = df.apply(tm.cleanTweets)
    return df

# def getTweetStream(amount_tweets) -> pd.DataFrame:
#     stream_tweets = tw.SearchStream().filter_by_keywords([keywords])
#     df = tw.TweetManipulation().listToDataFrame(stream_tweets)
#     return df

def sentimentAnalysis() :
    sent = sentiment.Sentiment()
    df = pd.DataFrame(columns=["Tweet","Subjectivity (in %)","Polarity"])
    df["Tweet"] = resultDF["Tweet"].copy()
    df["Subjectivity (in %)"] = df["Tweet"].apply(sent.getSubjectivity)
    df["Polarity"] = df["Tweet"].apply(sent.getPolarity)
    return df
    
    
# main
if submit_button:
    if tweet_kind == "History":
        resultDF = getTweetHistory(amount_tweets)
    elif tweet_kind == "Realtime":
        pass
        #resultDF = getTweetStream(amount_tweets)
    st.subheader("Tweet Data")
    st.dataframe(resultDF, width=1800, height=600)
    st.markdown("""---""")
    st.subheader("Sentiment Analysis")
    st.dataframe(sentimentAnalysis())


    
    
    
    