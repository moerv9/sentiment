# Imports
import streamlit as st
import matplotlib as mpl
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import sys
sys.path.append("../sent/")
import tweets
from ..sent import tweets
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
    
def pieChart(neg,pos,neut):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'Negative', 'Positive', 'Neutral'
    sizes = [neg, pos, neut] 
    colors = ["orangered",'mediumseagreen',"tab:gray"]
    explode = (0, 0.1, 0) 

    fig1, ax1 = plt.subplots()
    fig1.patch.set_alpha(0)
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True,colors=colors,textprops={'color':"w"})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)

def wordCloud(df):
    all_words = ' '.join([tweets for tweets in df['Tweet']])
    word_cloud = WordCloud(width=500, height=300, random_state=21, max_font_size=119).generate(all_words)

    plt.imshow(word_cloud, interpolation="bilinear")
    plt.axis('off')
    st.pyplot(plt)
    
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
    col1,col2,col3 = st.columns(3)
    with col1:
        st.dataframe(sentimentAnalysis()["Dataframe"])
    with col2:
        neg=sentimentAnalysis()["negative Tweets"]
        pos=sentimentAnalysis()["positive Tweets"]
        neut=sentimentAnalysis()["neutral Tweets"]
        st.write(f"Negative: {neg}, Positive: {pos}, Neutral: {neut}")
        pieChart(neg,pos,neut)
    with col3:
        wordCloud(resultDF)