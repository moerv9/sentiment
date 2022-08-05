import re
import multidict
from wordcloud import WordCloud,STOPWORDS
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from collections import Counter


my_stopwords={"amp","bitcoin","bitcoins","cardano"}
sentiment_model = SentimentIntensityAnalyzer()


def get_sent_meaning(sent_list):
    sent_meaning_list = []
    for num in sent_list:
        sent_meaning_list.append(conv_sent_score_to_meaning(num))
    #mean_avg = sum(sent_list) / len(sent_list)
    return sent_meaning_list

def conv_sent_score_to_meaning(num):
    if num > 0 and num <= 0.5:
        return("Positive")
    elif num > 0.5:
        return("Very Positive")
    elif num < 0 and num >= -0.5:
        return("Negative")
    elif num < - 0.5 :
        return("Very Negative")
    else:
        return("Neutral")


def getFrequencies_Sentiment(df):
    all_words = ' '.join([tweets for tweets in df])
    words = list(all_words.split(" "))
    cleaned_words = [x for x in words if not bool(re.search('\d|_|\$|\amp|\/', x))]
    cleaned_words = [re.sub(r"\.|\!|\,|\(|\)|\-|\?|\;|\\","",x) for x in cleaned_words]
    cleaned_words = [x for x in cleaned_words if not bool(re.search("you|my|your|if|me|so|do|us|see|im|a|the|an|the|to|in|for|of|or|by|with|is|on|that|be|it|he", x))]
    cleaned_words = [x for x in cleaned_words if not len(x)==1]
    
    wordcount = pd.value_counts(np.array(cleaned_words))
    df = pd.DataFrame(wordcount,columns=["Count"])
    df["Words"] = df.index
    df = df[["Words","Count"]].sort_values(by=["Count"],ascending=False)
    df.reset_index(drop=True, inplace=True)
    df["Signal"] = df["Words"].apply(trading_keywords)
    df = df.dropna(subset=["Signal"])
    
    grouped_df = df.groupby(by=["Signal"],as_index=False,sort=False).agg({"Count":"sum"})
    
    #sent_list = [sentiment_model.polarity_scores(words).get("compound") for words in df["Words"]] #Sent for each word
    #df["Sentiment"] = get_sent_meaning(sent_list)
    #df_count = df.groupby(df["Sentiment"], dropna=True).count() #count words for each sentiment "pos, neg, ..."
    
    return grouped_df #df,grouped_df,resampled_df

def get_signals(df,interval):
    df = df.filter(items=["Tweet"])
    df["Timestamp"] = df.index
    df.reset_index(drop=True,inplace=True)
    
    signals = df["Tweet"].apply(getFrequencies_Sentiment)#    df[["Signal","Count"]]
    
    #signal_dict = {key: df.loc[value] for key, value in df.groupby("Timestamp").groups.items()} 
    #df = df.groupby(by="Timestamp")
    #timegrouplist = [keys for keys in df.groupby("Timestamp").groups.keys()]
    #tweet_group_list = [df.loc[values] for values in df.groupby("Timestamp").groups.values()]
    
    return signals
 
    return pd.DataFrame(tweet_group_list)


def trading_keywords(word):
    if word in ["buy","up","bullish","bought","high","pump","growth","uptrend","revolution","hold","love","trust","bull","#pump","success","hodl"]:
        return "BUY"
    elif word in ["sell","down","bearish","sold","never","bad","low","dump","decline","downfall","downtrend","decay","recession","regess","short","hate","#short","#dump","loss","lost","lose"]:
        return "SELL"



def show_wordCloud(df):
    freq_words = getFrequencies_Sentiment(df)[0]
    wordcloud1 = WordCloud(relative_scaling=0.5,max_words=50,stopwords=my_stopwords,
                        width=500, height=250,collocations=False, random_state=1, max_font_size=100, background_color=None,colormap="viridis_r").generate_from_frequencies(freq_words)
    fig1 = plt.figure(figsize=(20, 10))
    fig1.patch.set_alpha(0)
    plt.imshow(wordcloud1, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(plt)