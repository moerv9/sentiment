'''
01_💬_Tweet-Sentiment.py
Main File to visualise all the data from tweets, sentiment and trades with Streamlit.
'''
from datetime import date
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_data import get_Heroku_DB, get_sent_percentage, resample_df, split_DF_by_time
from visualise import show_cake_diagram, show_trade_chart, show_wordCloud, visualise_word_signals,visualise_acc_balance
from financial_data import get_kucoin_data, get_signal_by_keywords,calc_pnl


st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )

count = st_autorefresh(interval=1000*60*5, key="sent")

@st.experimental_memo(show_spinner=True,suppress_st_warning=True,ttl=5*60)
#@st.cache(ttl=60*5,allow_output_mutation=True,show_spinner=True,suppress_st_warning=True)
def loading_data_from_heroku_database():
    df, df_trades, duplicates = get_Heroku_DB(today=False)
    df_trades.replace(df_trades[df_trades["id"]== 59]["usdt_balance"][0],2524.543209,inplace=True)
    df_trades.replace(df_trades[df_trades["id"]== 59]["btc_balance"][0],0.05575778,inplace=True)
    return df,df_trades, duplicates


with st.sidebar:
    st.write("Change Visibility")
    hide_explanation = st.checkbox(label="Hide Explanation",value=False)
    hide_most_important_metrics = st.checkbox(label="Hide most important metrics",value=False)
    hide_single_tweets = st.checkbox(label="Hide Last Collected Tweets",value=False)
    hide_sentiment = st.checkbox(label="Hide Sentiment Metrics",value=False)
    hide_Wordcloud_and_TweetSent = st.checkbox(label="Hide Word Analysis",value=False)
    hide_trades = st.checkbox(label="Hide Trades",value=False)
    hide_acc_balance = st.checkbox(label="Hide Account Balance",value=False)
    st.info("Turn on Darkmode in upper right settings!")
    st.info("Press 'R', if any error occurs.")
intervals = 60 

#Get Dataframes
#Convert Database to Dataframe
df, df_trades, duplicates  = loading_data_from_heroku_database()

st.subheader(f"{date.today().strftime('%d-%m-%Y')} - Bitcoin Sentiment Trading")

single_sent_scores_df,resampled_mean_tweetcount,mean_follower = resample_df(df, intervals, True, False)#(split_DF_by_time(df,lookback_timeframe),intervals,True)

last_avail_tweets_1h = split_DF_by_time(df,1,resampled_mean_tweetcount.index[0]) # gets all the last tweets from the last available timestamp - 1h


# explanation section
if not hide_explanation:
    st.subheader("Explanation")
    st.markdown("**This is a site to visualise a few metrics from the project: [Social Signal Sentiment-Based Prediction for Cryptocurrency Trading](https://github.com/moerv9/sentiment)**")
    st.write("The project aims to analyse the sentiment/opinion from tweets on Twitter about Bitcoin and converts these into trading-signals.")
    st.markdown(
                "The sentiment score is calculated by [vader](https://github.com/cjhutto/vaderSentiment) and is between -1 and 1. "
                "Values above 0.2 indicate a positive Sentiment and a Buy-Signal. Values below are negative and indicate a Sell-Signal.")
    st.write("Below you can have a look at different real-time metrics.")
    st.write("Click the checkboxes on the left sidebar to hide/show metrics.")
    st.markdown("---")

st.write("#")

# Most important metrics section
if not hide_most_important_metrics:
    st.subheader("Most important Metrics")
    col1,col2 = st.columns(2)
    current_time = resampled_mean_tweetcount.index[0]
    current_sent = resampled_mean_tweetcount["Avg"].head(1)
    current_sent_is = resampled_mean_tweetcount["Sent is"].head(1)[0]
    current_signal = resampled_mean_tweetcount["Signal"].head(1)[0]
    with col1:
        st.metric(label=f"Last collected Sentiment: {current_time}",value = round(current_sent,4),delta=current_sent_is,delta_color="off")
    with col2:
        st.metric(label="Current Signal",value=current_signal)
    st.markdown("---")


# section with dataframe for last collected tweets
if not hide_single_tweets:
    st.subheader("Last collected Tweets")
    rows = st.slider("Rows to retrieve:",step=5,min_value=5,max_value=500,value=5)
    st.dataframe(df.head(rows))
    st.markdown("---")

st.write("#")

# section for metrics of sentiment
if not hide_sentiment:
    st.subheader("Sentiment Metrics")
    col1,col2 = st.columns(2)
    col1.text("Last 4 days")
    col2.text("Last 24 hours")
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.metric(label=f"Collected Tweets", value=df.shape[0])
    with col2:
        st.metric(label="Deleted Duplicates",value=f"{int(duplicates/df.shape[0]*100)} %")
    with col3:
        st.metric(label = f"Collected Tweets", value = split_DF_by_time(df,24,False).shape[0])
    with col4:
        st.metric(label="Average Followers",value=int(mean_follower["Followers"].tail(1)))
    st.write("##")
    st.write("##")

    col1,col2 = st.columns(2)
    with col1:
        st.text("Tweet sentiment for the last hour")
        #st.dataframe(percentage_btc_df)
        show_cake_diagram(df = get_sent_percentage(last_avail_tweets_1h,False),which = "percentage")
    with col2:
        st.text(f"Last Periods with Average Sentiment and total amount of Tweets")
        st.dataframe(resampled_mean_tweetcount.head(5))
        #visualise_timeperiods(resampled_mean_tweetcount.head(5))
    st.markdown("---")

st.write("#")

# section for word analysis
if not hide_Wordcloud_and_TweetSent:
    st.subheader("Word Analysis")
    signal_by_keywords_df = get_signal_by_keywords(last_avail_tweets_1h)
    col1,col2,col3 = st.columns(3)   
    with col1:
        st.text("Most used Words in the last hour")
        show_wordCloud(last_avail_tweets_1h,True)
    with col2:
        st.text("Most used Words that indicate Buy or Sell")
        visualise_word_signals(signal_by_keywords_df[0])
    with col3:
        st.text("Total Proportions")
        show_cake_diagram(df = signal_by_keywords_df[1],which="signal count")
    st.markdown("---")
    
st.write("#")
# section for trades
if not hide_trades:
    last_trade_time = df_trades["tradeAt"][0]#df_trades.index[0]
    second_last_avg = resampled_mean_tweetcount.head(2).iloc[1]
    st.subheader(f"Last Trade at: {str(last_trade_time)[:-10]}")
    sum_fees = round(df_trades["fee"].sum(),2)
    st.text("Account Metrics")
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        st.metric(label="Starting USDT Balance", value="5000 $")
    with col2:
        st.metric(label = f"Current USDT Holdings", value = f"{int(get_kucoin_data()[0])} $")
    with col3:
        st.metric(label="Current BTC Holdings",value=f"{get_kucoin_data()[1]} ₿")
    with col4:
        st.metric(label="Executed Trades",value=df_trades.shape[0])
    with col5:
        st.metric(label="Total Fees",value = f"{sum_fees} $")
        
    st.write("#")
    st.text("Current BTC Holdings")
    col1,col2,col3,col4 = st.columns(4)
    with col1: 
        st.metric(label="Current BTC Price",value=f"{get_kucoin_data()[5]} $")
    with col2:
        st.metric(label="Holdings with real BTC Price",value=f"{get_kucoin_data()[4]} $")
    with col3:
        st.metric(label="Sandbox BTC Price",value=f"{get_kucoin_data()[2]} $")
    with col4:
        st.metric(label="Holdings with Sandbox Price" ,value=f"{get_kucoin_data()[3]} $")

    st.write("#")
    st.subheader("Last Trades")
    time_frame = 24
    try:
        show_trade_chart(split_DF_by_time(df_trades,96,False))
    except Exception as e:
        st.warning("Price Data couldn't be displayed. Reloading with 'R' might fix it.")
        print(f"Chart Exception: {e}")
    st.write("#")
    with st.expander("Show Trade List"):
        st.text("Last Trades")
        important_df_trades = df_trades
        important_df_trades["avg from"] = important_df_trades.index
        important_df_trades.index = important_df_trades["side"]
        important_df_trades = important_df_trades[["tradeAt","usdt_balance","btc_balance","fee","avg","avg from"]]
        rows = st.slider(label="",min_value = 1,value=5,max_value = len(important_df_trades))
        st.dataframe(important_df_trades.head(rows))
    st.markdown("---")

st.write("#")

if not hide_acc_balance:
    st.subheader("Account Balance")
    pnl_df = calc_pnl(df_trades)
    visualise_acc_balance(pnl_df)
    st.write("#")
    with st.expander("Show Account Balance Table"):
        st.dataframe(pnl_df)
    
        




