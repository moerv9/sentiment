import psycopg2
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
import logging
from datetime import date, time, timedelta,datetime
from logging.handlers import RotatingFileHandler

from time import sleep
from streamlit_autorefresh import st_autorefresh
from dateutil import tz
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
from words import get_sent_meaning,conv_sent_score_to_meaning
from financial_data import getminutedata


logger = logging.getLogger(__name__)

# Config
#os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment")
from config import ConfigDB

#Uncomment for Streamlit Deployment 
#DB_URL = st.secrets["DB_URL"]
#Uncomment for local Dev
DB_URL = ConfigDB().DB_URL



def split_DF_by_time(df,time_frame):
    """Returns Dataframe for the past hours specified in time_frame

    Args:
        df (_type_): Dataframe to split
        time_frame (_type_): timeframe to look at

    Returns:
        DataFrame: in the given timeframe
    """
    #print("split df by time:")
    #print(df.head(10))
    if "Timestamp" in df.columns:
        df.index = df["Timestamp"]
    df.index = pd.to_datetime(df.index)
    timedelt = datetime.now() - timedelta(hours=time_frame,minutes=15)
    mask = (df.index > timedelt)
    df = df.loc[mask]
    return df

def get_Heroku_DB(today=True):
    conn = psycopg2.connect(DB_URL, sslmode="require")
    if today:
        limit=60000
        query = f"select * from tweet_data where Tweet_Date > current_date order by id desc limit {limit};"
    else:
        st.info("This may take a while...")
        query = f"select * from tweet_data order by id desc limit 1000000;"
    df = pd.read_sql(query, conn)
    columns = {"body": "Tweet",
                "keyword": "Keyword",
                "tweet_date": "Timestamp",
                "location": "Location",
                "verified_user": "User verified",
                "followers": "Followers",
                "user_since": "User created",
                "sentiment": "Sentiment Score",
                }
    #df = df.drop(columns=["sentiment_meaning"])
    df = df.rename(columns=columns)
    df.index = df["Timestamp"]
    print("get herokuDB:")
    print(df.index.to_datetime().strftime("%Y-%m-%dT%H:%M:%S %Z:%z"))
    df.drop(columns=["Timestamp"],inplace=True)
    df.index = df.index + timedelta(hours=2)
    rows = df.shape[0]
    duplicates = list(df.index[df.duplicated(subset=["Tweet"],keep=False)])
    df.drop(labels=duplicates,inplace=True)
    print(f"Deleted {len(duplicates)} duplicates from a total of {rows}")
    return df


def calc_mean_sent(df, min_range,filter_neutral=False):
    if filter_neutral:
        df = df[df["Sentiment Score"] != 0.0]
    sent_meaning_list = get_sent_meaning(df["Sentiment Score"]) #Sentiment Values to Meaning ("Positive,Negative,etc.")
    sent_meaning_df = pd.Series(sent_meaning_list)
    sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())
    
    df = df.filter(items=["Sentiment Score"]) #Keep only "Sentiment Score" Column
    #df = df.groupby(df.index, dropna=True).mean() #Group by timestamp and calc mean sentiment
    df.rename(columns={"Sentiment Score": "Avg. Sentiment"},inplace=True)
    count_tweets = df.resample(f"{min_range}T").count() #count Tweets
    count_tweets.rename(columns={"Avg. Sentiment":"Total Tweets"},inplace=True)
    df = df.resample(f"{min_range}T").mean()

    #sent_meaning_for_avg = pd.DataFrame(get_sent_meaning(df["Avg. Sentiment"]),columns=["Sent is"]) #no idea why this adds all the rows below and not next to it
    
    new_df = pd.concat([df,count_tweets],axis="columns").sort_index(ascending=False) #Put all DF together
    
    # sent_meaning_df = pd.Series(sent_meaning_list)
    # sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())
    # sent_appearances["Sentiment"] = sent_appearances.index
    # sent_appearances.rename(columns={0:"Tweets"},inplace=True)
    # sent_appearances = sent_appearances[["Sentiment","Tweets"]]
    # sent_percentages = pd.Series([int((num/len(sent_meaning_df))*100) for num in sent_appearances["Tweets"]])
    # sent_appearances_df = pd.concat([sent_appearances.reset_index(drop=True),sent_percentages.reset_index(drop=True)],axis=1)
    # sent_appearances_df.rename(columns={0:"Percentage"},inplace=True)
    
    #print(sent_appearances_df[sent_appearances_df["Sentiment"] == "Positive"]["Percentage"])
    #df["Positive (%)"] = sent_appearances_df[sent_appearances_df["Sentiment"] == "Positive"]["Percentage"]

    # sent_app_transposed = sent_appearances_df.transpose(copy=True)
    # print(sent_app_transposed)
    #sent_app_transposed["Sentiment"] = str(sent_app_transposed["Sentiment"])
    return pd.DataFrame(new_df), sent_appearances

def get_decision_df(df,time_range, filter_neutral=False):
    if filter_neutral:
        df = df[df["Sentiment Score"] != 0.0]
    df = df.filter(items=["Sentiment Score"])

    mean_df = df.resample(f"{time_range}Min").mean().sort_index(ascending=False)
    mean_df.rename(columns={"Sentiment Score" : "Mean"},inplace=True)
    
    df["Sent is"] = df["Sentiment Score"].apply(conv_sent_score_to_meaning)
    mean_df["Sent is"] = mean_df["Mean"].apply(conv_sent_score_to_meaning)
    
    
    #df["Positive Tweets (%)"] = df["Sent is"].apply(count_sents)
    #total_sent_count = pd.value_counts(np.array(df["Sent is"].tolist()))
    #TODO: resamplen für zeitraum und in diesem die werte für "positive,etc" zählen
    #TODO: resamplen für average
    
    return df, mean_df


def count_sents(vals):
    pass
    wordcount = pd.value_counts(np.array(vals))
    df = pd.DataFrame(wordcount,columns=["Count"])
    #return wordcount


# CHARTS
def show_sentiment_chart(df, label, color,intervals,lookback_timeframe,symbol):
    #setup
    fig, axs = plt.subplots(2,1,sharex=True,constrained_layout=True)#figsize=(10, 4))
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.rcParams['font.size'] = '8'
    #colors
    for nn,ax in enumerate(axs):
        axs[nn].title.set_color("white")
        axs[nn].xaxis.label.set_color('white') 
        axs[nn].yaxis.label.set_color('white')
        axs[nn].tick_params(axis='x', colors='white')
        axs[nn].tick_params(axis='y', colors='white')
        axs[nn].spines["left"].set_color('white')
        axs[nn].spines["bottom"].set_color('white') 
        axs[nn].spines["top"].set_alpha(0)
        axs[nn].spines["right"].set_alpha(0)
        axs[nn].set_facecolor((0,0,0,0))
        axs[nn].xaxis.set_major_locator(locator)
        axs[nn].xaxis.set_major_formatter(formatter)
    fig.patch.set_alpha(0)
    
    #set labels
    axs[0].set_title(f"Average Sentiment for {intervals} Min. Intervals")
    axs[0].set_ylabel("Sentiment Score")
    axs[1].set_title(f"Price for {label}")
    axs[1].set_xlabel("Time")
    axs[1].set_ylabel("Price ($)")
    
    #first plot for sentiment
    #axs[0].scatter(x,y, label=label,color=color1,edgecolor="none")#markerfacecolor="white")
    axs[0].plot(df, label=label,color=color, markersize=5) #markerfacecolor="white")

    #second plot for price
    data = getminutedata(symbol,intervals,lookback_timeframe)
    x1 = data.index
    y1 = data.Close
    axs[1].plot(x1,y1,color=color,markersize=5)
    #plt.gcf().autofmt_xdate()
    #plt.tight_layout()
    #plt.legend()
    #plt.show()    
    st.pyplot(fig)

def show_cake_diagram(df):
    labels = [i for i in df["Sentiment"]]
    sizes = [i for i in df["Percentage"]]
    colors = ['#99ff99','#66b3ff','#ff9999','#ffcc99','#ff99cc']
    fig1, ax1 = plt.subplots()
    patches,texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',  startangle=90,colors=colors,radius=.3)#textprops=dict(color="w"),shadow=True,
    for text in texts:
        text.set_color('white')
    for autotext in autotexts:
        autotext.set_color('grey')
    #plt.rcParams['figure.facecolor'] = (0.5, 0.0, 0.0, 0.5)
    #fig1.set_facecolor(color=None)
    fig1.patch.set_alpha(0)
    ax1.axis('equal')
    ax1.set_title("Positive Tweets")
    plt.setp(autotexts, size=14, weight="bold")
    plt.tight_layout()
    #plt.show()
    st.pyplot(plt)
    
#TODO
# def show_bar_chart(df):
#     sizes = [i for i in df["Percentage"]]
#     labels = [i for i in df["Sentiment"]]
#     plt.rcParams['figure.facecolor'] = (0, 0.0, 0.0, 0)
#     fig1, ax = plt.subplots()
#     ax.bar(1,sizes[0])
#     ax.bar(1,sizes[1])
#     plt.tight_layout()
#     st.pyplot(plt)


