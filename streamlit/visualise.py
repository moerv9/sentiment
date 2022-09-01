'''
visualise.py
Functions to visualise the price chart and words.
'''
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator,AutoMinorLocator,MaxNLocator,AutoLocator,AutoMinorLocator)
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from financial_data import getminutedata
from wordcloud import WordCloud,STOPWORDS

my_stopwords={"amp","the","and","to","it","as","a","an","in","by","is","that","be","of","or","on","its","at","you","this","for","with","has","what","i","will","just","eth","bitcoin","bnb","ethereum","cardano","btc","usdt","my","crypto","cryptocurrency","we","if","from"}

cmap = plt.cm.get_cmap("turbo")#('RdYlBu')
date_locator = mdates.AutoDateLocator(minticks=10, maxticks=20)
formatter = mdates.ConciseDateFormatter(date_locator)
#xtick_formatter = mdates.AutoDateFormatter(date_locator)
#cut_date_format = mdates.DateFormatter('%d-%m %H:%M')
    
def show_trade_chart(df):
    """Visualise the trades

    Args:
        df (DataFrame): Avg, Side, Timestamp
        
    Returns:
        Streamlit Plot: Trades with Bitcoin Chart
    """
    plt.clf()
    fig1, ax1 = plt.subplots(figsize=(8,4))
    ax1.xaxis.label.set_color('white') 
    ax1.yaxis.label.set_color('white')
    ax1.tick_params(axis='y', colors='white')
    ax1.tick_params(axis='x', colors='white',labelrotation=30)
    ax1.spines["left"].set_color('white')
    ax1.spines["bottom"].set_color('white')
    ax1.spines["top"].set_alpha(0)
    ax1.spines["right"].set_alpha(0)
    ax1.set_facecolor((0,0,0,0))
    fig1.patch.set_alpha(0)
    ax1.xaxis.set_major_locator(date_locator)
    ax1.xaxis.set_minor_locator(date_locator)
    ax1.xaxis.set_major_formatter(formatter)
    
    ax1.set_ylabel("Price ($)")
    
    trade_timeperiods = df.filter(items=["side"]) #.values um die tradeAt zu bekommen
    data = getminutedata("BTCUSDT",1,96)
    di = data.index
    dc = data.Close
    lst = []
    sell = []
    buy = []
    # print(f"len di: {len(di)}")
    # print(f"len tt: {len(trade_timeperiods)}")
    for i in range(len(di)):
        if di.values[i] in trade_timeperiods.index:
            lst.append(dc.values[i])

    for y in range(len(trade_timeperiods)):
        if trade_timeperiods["side"][y] == "sell":
            sell.append(y)
        elif trade_timeperiods["side"][y] == "buy":
            buy.append(y)
            
    ax1.plot(trade_timeperiods.index, lst, label = "BTC Price",color = "w",linewidth = 1)
    ax1.plot(trade_timeperiods.index, lst, "v", label = "sell",color = cmap(0.8),markersize = 4,markevery = sell)
    ax1.plot(trade_timeperiods.index, lst, "^", label = "buy",color = cmap(0.25),markersize = 4,markevery = buy)

    fig1.autofmt_xdate()
    ax1.legend()
    st.pyplot(fig1)
    
def visualise_acc_balance(df):
    """Visualse Account Balances over Trades.

    Args:
        df (DataFrame): Trade Dataframe. 
    """
    plt.clf()
    fig1, ax1 = plt.subplots(figsize=(8,4))
    ax1.xaxis.label.set_color('white') 
    ax1.yaxis.label.set_color('white')
    ax1.tick_params(axis='y', colors='white')
    ax1.tick_params(axis='x', colors='white',labelrotation=30)
    ax1.spines["left"].set_color('white')
    ax1.spines["bottom"].set_color('white')
    ax1.spines["top"].set_alpha(0)
    ax1.spines["right"].set_alpha(0)
    ax1.set_facecolor((0,0,0,0))
    fig1.patch.set_alpha(0)
    ax1.xaxis.set_major_locator(date_locator)
    ax1.xaxis.set_minor_locator(date_locator)
    ax1.xaxis.set_major_formatter(formatter)

    ax1.set_ylabel("Price ($)")
    
    ax1.plot(df.index, df.acc_binance_balance, label = "Acc. Balance (Binance Price)",color = cmap(0.68),linewidth = 1)
    ax1.plot(df.index, df.acc_kucoin_balance, label = "Acc. Balance (Kucoin Price)",color = cmap(0.35),linewidth = 1)
    ax1.axhline(y=5000,linestyle=":",color=cmap(0.15),linewidth=0.5)   
    
    fig1.autofmt_xdate()
    ax1.legend()
    st.pyplot(fig1)

def show_cake_diagram(df, which):
    """Show Cake Diagram for either the percentages or the signal count

    Args:
        df (DataFrame): Sentiments, Percentage
        which (String): "percentage" or "signal count"
    """
    lst = df.values.tolist()
    if which == "percentage":
        for i in range(len(lst)):
            if lst[i][0] == "Positive":
                lst[i].append(cmap(0.25))
            elif lst[i][0] == "Very Positive":
                lst[i].append(cmap(0.15))
            elif lst[i][0] == "Negative":
                lst[i].append(cmap(0.8))#("#f7ff99")
            elif lst[i][0] == "Very Negative":
                lst[i].append(cmap(0.9))
            elif lst[i][0] == "Neutral":
                lst[i].append(cmap(0.55))
        labels = [i[0] for i in lst]
        sizes = [i[2] for i in lst]
        colors = [i[3] for i in lst]
        
    elif which == "signal count":
        for i in range(len(lst)):
            if lst[i][0] == "BUY":
                lst[i].append(cmap(0.25))
            else:
                lst[i].append(cmap(0.8))
        labels = [i[0] for i in lst]
        sizes = [i[1] for i in lst]
        colors = [i[2] for i in lst]

    fig1, ax1 = plt.subplots()
    patches, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',  startangle=90,colors=colors,radius=.3)
    for text in texts:
        text.set_color('white')
    for autotext in autotexts:
        autotext.set_color('white')

    fig1.patch.set_alpha(0)
    ax1.axis('equal')
    plt.setp(autotexts, size=10) #weight="bold"
    plt.setp(texts, size=10) #weight="bold"
    plt.tight_layout()
    st.pyplot(plt)
    
def visualise_word_signals(df):
    """Words that signal buy or sell

    Args:
        df (DataFrame): Words, Count 
        
    Returns:
        Plot: Barchart with Words, 
    """
    lst = df.values.tolist()
    for i in range(len(lst)):
        if lst[i][2] == "BUY":
            lst[i].append(cmap(0.25))
        else:
            lst[i].append(cmap(0.8))
    labels = [i[0] for i in lst]
    count = [i[1] for i in lst]
    buy_or_sell = [i[2] for i in lst]
    colors = [i[3] for i in lst]
    
    fig1, ax1 = plt.subplots()
    ax1.xaxis.label.set_color('white') 
    ax1.yaxis.label.set_color('white')
    ax1.tick_params(axis='y', colors='white')
    ax1.tick_params(axis='x', colors='white')
    ax1.spines["left"].set_color('white')
    ax1.spines["bottom"].set_color('white')
    ax1.spines["top"].set_alpha(0)
    ax1.spines["right"].set_alpha(0)
    ax1.set_facecolor((0,0,0,0))
    fig1.patch.set_alpha(0)
    ax1.set_xlabel("Count")
    #ax1.xaxis.set_ticks(range(len(labels)))
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax = ax1.barh(labels,width=count,color = colors, height=0.7)
    ax1.invert_yaxis()
    ax1.bar_label(ax,label_type="center",color="white")
    buy_patch = mpatches.Patch(color=cmap(0.25), label='Buy-Signal')
    sell_patch = mpatches.Patch(color=cmap(0.8), label='Sell-Signal')
    plt.legend(handles=[buy_patch,sell_patch])
    #plt.tight_layout()
    #ax1.xaxis.set_major_locator(AutoLocator())
    #ax1.xaxis.set_major_formatter(formatter)
    st.pyplot(plt)
    

def show_wordCloud(df,df_contains_tweet):
    """WordCloud for Tweet Words.
    Visualise the amount of words used in tweets.

    Args:
        df (DataFrame): Df with Frequencies
        df_contains_tweet (DataFrame): Df with single Tweets
    """
    if df_contains_tweet:
        all_words = ' '.join([tweets for tweets in df["Tweet"]])

        wordcloud1 = WordCloud(relative_scaling=0.5,max_words=50,stopwords=my_stopwords,
                            width=700, height=350,collocations=False, random_state=1, max_font_size=100, background_color=None,colormap="turbo").generate(all_words) #viridis_r
    elif df_contains_tweet == False:
        df.reset_index(drop=True, inplace=True)
        df.index = df["Words"] 
        df = df.drop(columns=["Signal","Words"])
        wordcloud1 = WordCloud(relative_scaling=0.5,max_words=50,stopwords=my_stopwords,
                            width=700, height=450,collocations=False, random_state=1, max_font_size=100, background_color=None,colormap="viridis_r").generate_from_frequencies(df)
    fig1 = plt.figure()
    fig1.patch.set_alpha(0)
    plt.imshow(wordcloud1, interpolation="bilinear")
    plt.axis('off')
    plt.tight_layout(pad=0)
    st.pyplot(plt)
    
