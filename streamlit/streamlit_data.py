'''
streamlit_data.py
Functions to edit the data from the databases: Splitting the Dataframe, calculate average and convert to signals.
'''
import psycopg2
import pandas as pd
import logging
from datetime import timedelta, datetime
from financial_data import get_signal_by_sent_score
import streamlit as st

logger = logging.getLogger(__name__)

# Config
#os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment")
from config import ConfigDB

#Uncomment for Streamlit Deployment 
#DB_URL = st.secrets["DB_URL"]
#Uncomment for local Dev
DB_URL = ConfigDB().DB_URL


def get_sent_meaning(sent_list):
    """Apply the function to convert the sentiment scores to a meaning like "positive, negative, ..." to a whole column

    Args:
        sent_list (Column): Dataframe Column to apply function to

    Returns:
        list: Sentiment Meaning
    """
    sent_meaning_list = []
    for num in sent_list:
        sent_meaning_list.append(conv_sent_score_to_meaning(num))
    return sent_meaning_list

def conv_sent_score_to_meaning(num):
    """convert number to sentiment meaning

    Args:
        num (float): sentiment score
    """
    if num > 0.2 and num <= 0.6:
        return("Positive")
    elif num > 0.6:
        return("Very Positive")
    elif num <= 0.20 and num >= -0.6:
        return("Negative")
    elif num < - 0.6 :
        return("Very Negative")
    else:
        return("Neutral")


def get_Heroku_DB(today=True):
    """Get Tweet and Trade Data from Heroku Database and delete Duplicates.

    Args:
        today (bool, optional): Get only data for today. Defaults to True.

    Returns:
        df: Get DF for Tweets and the Trades. 
    """
    conn = psycopg2.connect(DB_URL, sslmode="require")
    if today:
        limit=60000
        logger.info("Getting data from Today")
        query = f"select * from tweet_data where Tweet_Date > current_date order by id desc limit {limit};"
    else:
        #logger.info("Getting data from past Today")
        query = f"select * from tweet_data where Tweet_Date > current_date - interval '4' day order by id desc limit 1000000;"
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
    df.drop(columns=["Timestamp"],inplace=True)
    df.index = df.index + timedelta(hours=2)
    df.index = df.index.floor("Min")
    #print(df.index.tz_localize("Europe/Berlin"))
    rows = df.shape[0]
    duplicates = list(df.index[df.duplicated(subset=["Tweet"],keep=False)])
    df.drop_duplicates(subset=["Tweet"],keep=False,inplace=True)

    #print(f"Deleted {len(duplicates)} duplicates from a total of {rows}")
    
    query = "select * from trade_data where id > 28 order by id desc;"
    df_trades = pd.read_sql(query, conn)
    #df_trades = df_trades.rename(columns={"avg": "Avg"})
    df_trades.index = df_trades["avgTime"]
    df_trades.index = df_trades.index + timedelta(hours=2)
    df_trades.drop(columns=["avgTime"],inplace=True)

    return df.sort_index(ascending=False), df_trades, len(duplicates)

def split_DF_by_time(df,time_frame,timestamp):
    """Returns Dataframe for the past hours specified in time_frame

    Args:
        df (_type_): Dataframe to split
        time_frame (_type_): timeframe to look at

    Returns:
        DataFrame: in the given timeframe
    """
    if "Timestamp" in df.columns:
        df.index = df["Timestamp"]
    df.index = pd.to_datetime(df.index)
    if timestamp == False:
        timedelt = datetime.now() - timedelta(hours= time_frame)
    else:
        timedelt = timestamp - timedelta(hours= time_frame)
        mask = (df.index < pd.to_datetime(timestamp))
        df = df.loc[mask]
    mask = (df.index > timedelt)
    df = df.loc[mask]
    return df

def get_sent_percentage(df, filter_neutral=False):
    """Get the Percentage for all Sentiments (pos,neg)

    Args:
        df (_type_): _description_
        filter_neutral (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if filter_neutral:
        df = df[df["Sentiment Score"] != 0.0]
    sent_meaning_list = get_sent_meaning(df["Sentiment Score"]) #Sentiment Values to Meaning ("Positive,Negative,etc.")
    sent_meaning_df = pd.Series(sent_meaning_list)
    sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())  
    
    sent_meaning_df = pd.Series(sent_meaning_list)
    sent_appearances = pd.DataFrame(sent_meaning_df.value_counts())
    sent_appearances["Sentiment"] = sent_appearances.index
    sent_appearances.rename(columns={0:"Tweets"},inplace=True)
    sent_appearances = sent_appearances[["Sentiment","Tweets"]]
    sent_percentages = pd.Series([int((num/len(sent_meaning_df))*100) for num in sent_appearances["Tweets"]])
    sent_appearances_df = pd.concat([sent_appearances.reset_index(drop=True),sent_percentages.reset_index(drop=True)],axis=1)
    sent_appearances_df.rename(columns={0:"Percentage"},inplace=True)
    # print("Sent appearencs")
    # print(sent_appearances_df[sent_appearances_df["Sentiment"] == "Positive"]["Percentage"])
    # df["Positive (%)"] = sent_appearances_df[sent_appearances_df["Sentiment"] == "Positive"]["Percentage"]
    # sent_app_transposed = sent_appearances_df.transpose(copy=True)
    # print("sent transposed")
    # print(sent_app_transposed)

    return sent_appearances_df

def resample_df(df,interval, filter_neutral=False,by_day=False):
    """Resample DFs: Single Tweets with Sentiment,
    Average Sent for 1h intervals, 
    Get Average Follower Count

    Args:
        df (DataFrame): _description_
        interval (integer): _description_
        filter_neutral (bool, optional): Filter neutral Tweets. Defaults to False.
        by_day (bool, optional): Get only for one day. Defaults to False.

    Returns:
        df : Sentiment for single Tweets
        resampled_mean_tweetcount : Avg Tweets, Total Tweets and Signal
        mean_follower : Average Followers for 1h
    """
    if filter_neutral:
        df = df[df["Sentiment Score"] != 0.0]
        
    df_follower = df.filter(items=["Followers"])
    mean_follower = df_follower.resample("1H",label="right").mean()
    df = df.filter(items=["Sentiment Score"])
    
    if by_day:
        count_tweets = df.resample(f"D",label="right").count()
        mean_df = df.resample(f"D",label="right").mean().sort_index(ascending=False)
    elif by_day == False:
        count_tweets = df.resample(f"1H",label="right").count()#count Tweets
        mean_df = df.resample(f"{interval}T",label="right").mean().sort_index(ascending=False)
        
    count_tweets.rename(columns={"Sentiment Score" : "Total Tweets"},inplace=True)
    mean_df.rename(columns={"Sentiment Score" : "Avg"},inplace=True)
    df["Sent is"] = df["Sentiment Score"].apply(conv_sent_score_to_meaning)
    mean_df["Sent is"] = mean_df["Avg"].apply(conv_sent_score_to_meaning)
    
    resampled_mean_tweetcount = pd.concat([mean_df,count_tweets],axis="columns")
    resampled_mean_tweetcount = resampled_mean_tweetcount.dropna(subset=["Avg"])
    resampled_mean_tweetcount["Signal"] = resampled_mean_tweetcount["Avg"].apply(get_signal_by_sent_score)
    pd.set_option('max_colwidth', 400)
    
    return df.sort_index(ascending=False), resampled_mean_tweetcount.sort_index(ascending=False), mean_follower
