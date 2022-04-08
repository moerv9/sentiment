# Imports
import streamlit as st
import matplotlib.pyplot as plt
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
        amount_tweets = st.slider("Amount of Tweets to return", min_value=1,max_value=100,value=10)
        form_keywords = st.text_input("Keywords", placeholder="Seperate by comma").split(",")
        btc_keywords = st.checkbox("btc")
        submit_button = st.form_submit_button(label='Get Data')
        

# Functions
@st.cache
def getTweetHistory(amount_tweets) -> pd.DataFrame: 
    if btc_keywords:
        keywords = ["btc","bitcoin","BTC"] 
    else:
        keywords = form_keywords
    historical_tweets = tweets.SearchTwitterHistory().filter_by_keywords("search_tweets","mixed",keywords,amount_tweets)
    tm = tweets.TweetManipulation()
    df = tm.listToDataFrame(historical_tweets)
    return df

# def getTweetStream(amount_tweets) -> pd.DataFrame:
#     stream_tweets = tw.SearchStream().filter_by_keywords([keywords])
#     df = tw.TweetManipulation().listToDataFrame(stream_tweets)
#     return df
@st.cache
def sentimentAnalysis():
    sent = sentiment.Sentiment()
    df = pd.DataFrame(columns=["Tweet","Subjectivity (in %)","Polarity"])
    df["Tweet"] = resultDF["Tweet"].copy()
    df["Subjectivity (in %)"] = df["Tweet"].apply(sent.getSubjectivity)
    df["Polarity"] = df["Tweet"].apply(sent.getPolarity)
    neg,pos,neut = sent.negative_count,sent.positive_count,sent.neutral_count
    return {"Dataframe" : df, "negative Tweets" : neg, "positive Tweets" : pos, "neutral Tweets" : neut}
    
def pieChart():
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
    sizes = [15, 30, 45, 10] 
    explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

# main
if submit_button:
    if tweet_kind == "History":
        resultDF = getTweetHistory(amount_tweets)
    elif tweet_kind == "Realtime":
        pass
        #resultDF = getTweetStream(amount_tweets)
    st.subheader("Tweet Data")
    st.dataframe(resultDF)
    st.markdown("""---""")
    st.subheader("Sentiment Analysis")

    st.dataframe(sentimentAnalysis()["Dataframe"])
    st.write("Negative: {neg}, Positive: {pos}, Neutral: {neut}".format(
        neg=sentimentAnalysis()["negative Tweets"],
        pos=sentimentAnalysis()["positive Tweets"],
        neut=sentimentAnalysis()["neutral Tweets"]))
    



    
    
    
    