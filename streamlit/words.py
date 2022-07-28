import re
import multidict
from wordcloud import WordCloud,STOPWORDS
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import streamlit as st

my_stopwords={"amp","bitcoin","bitcoins","cardano"}
sentiment_model = SentimentIntensityAnalyzer()

def get_sent_meaning(sent_list):
    sent_meaning_list = []
    for num in sent_list:
        sent_meaning_list.append(conv_sent_score_to_meaning(num))
    #mean_avg = sum(sent_list) / len(sent_list)
    return sent_meaning_list

def conv_sent_score_to_meaning(num):
    if num > 0.2 and num < 0.6:
        return("Positive")
    elif num > 0.6:
        return("Very Positive")
    elif num < - 0.2 and num > -0.6:
        return("Negative")
    elif num < - 0.6 :
        return("Very Negative")
    else:
        return("Neutral")


def getFrequencies_Sentiment(df):
    all_words = ' '.join([tweets for tweets in df['Tweet']])
    words = list(set(all_words.split(" ")))
    #set_words = [i for i in words if i not in my_stopwords] #if not bool(re.search('\d|_|\$', i)
    cleaned_words = [x for x in words if not bool(re.search('\d|_|\$|\amp', x))]
    cleaned_words = [re.sub(r"\.|\!|\,|\(|\)|\-|\?|\;|\\|\'","",x) for x in cleaned_words]
    #count_words = [cleaned_words.count(i) for i in cleaned_words]
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}
    # making dict for counting frequencies
    for text in cleaned_words:
        if re.match("a|the|an|the|to|in|for|of|or|by|with|is|on|that|be", text):
            continue
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    for key in tmpDict:
        fullTermsDict.add(key, tmpDict[key])
    del fullTermsDict[""]
    df = conv_FrequenciesToDF(fullTermsDict)
    return fullTermsDict, df

def conv_FrequenciesToDF(freq_Dict):
    df = pd.DataFrame.from_dict(freq_Dict,orient="index",columns=["Count"])
    df["Words"] = df.index
    df = df[["Words","Count"]]
    df.reset_index(drop=True, inplace=True)
    df = df.sort_values(by=["Count"],ascending=False)
    sent_list = [sentiment_model.polarity_scores(words).get("compound") for words in df["Words"]]
    df["Sentiment"] = get_sent_meaning(sent_list)
    return df

def show_wordCloud(df):
    freq_words = getFrequencies_Sentiment(df)[0]
    words = WordCloud(relative_scaling=0.5,max_words=50,stopwords=my_stopwords,
                        width=500, height=250,collocations=False, random_state=1, max_font_size=100, background_color=None,colormap="viridis_r").generate_from_frequencies(freq_words)
    fig1 = plt.figure(figsize=(20, 10))
    fig1.patch.set_alpha(0)
    plt.imshow(words, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(plt)