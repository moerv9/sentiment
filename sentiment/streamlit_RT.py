import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os, datetime, logging, time
from logging.handlers import RotatingFileHandler

#os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment")
from config_sent import ConfigAPI, ConfigDB
newconf = ConfigAPI()
api = newconf.create_api("auth1")


log_dir = 'Logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_name = '{}_stream.log'.format(datetime.date.today().strftime('%Y%m%d'))
log_handler = RotatingFileHandler(filename=os.path.join(log_dir, log_name), maxBytes=20000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                    datefmt='%d-%m-%Y T%H:%M:%S')

st.set_page_config(
    page_title="RealTime Tweet Data", 
    )
st.title("View Dataset from Livestream")

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_con():
    return create_engine('postgresql://{}:{}@{}/tweets'.format(ConfigDB.USER, ConfigDB.PASS, ConfigDB.HOST),convert_unicode=True)

@st.cache(allow_output_mutation=True,show_spinner=False, ttl=5*60)
def get_data():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df = pd.read_sql_table("tweets",get_con())
    df = df.rename(columns={"body": "Tweet", "tweet_date":"Timestamp", 
        "followers": "Followers", "sentiment": "Sentiment", "keyword": "Keyword",
        "verified_user": "User verified"})
    return df, timestamp

def wordCloud(df):
    try:
        all_words = ' '.join([tweets for tweets in df['Tweet']])
    except:
        print(Exception)
        pass
    word_cloud = WordCloud(width=500, height=300, random_state=21, max_font_size=119).generate(all_words)

    plt.imshow(word_cloud, interpolation="bilinear")
    plt.axis('off')
    st.pyplot(plt)
    


#get excel and sheet names, sheet name = sentiment average
tabs:list = pd.ExcelFile("26-04-2022_stream.xlsx").sheet_names
slider_value = st.slider("Choose Sheet",min_value= 1,max_value=len(tabs))
dict_df = pd.read_excel("26-04-2022_stream.xlsx",sheet_name=None)
sent_avg = float(tabs[slider_value-1])

if sent_avg >0.1:
    sent_avg_eval = "Positive"
elif sent_avg <-0.1:
    sent_avg_eval = "Negative"
else:
    sent_avg_eval = "Neutral"

df = pd.DataFrame(dict_df[tabs[slider_value-1]])
time_col = df["Time"].values
time = st.text(f"Duration: '{time_col[0]}'  ->  '{time_col[-1]}'")
st.dataframe(df.head(5))
df.style.hide(level = 1)  
st.markdown("---")

def add_together(tabs):
    list = [names for names in tabs]
    return list

#print(add_together(tabs))
    
if st.slider:
    st.text(f"Rows: {len(df)}")
    st.subheader = "Metrics"
    st.metric("Sentiment is",sent_avg_eval,f"{sent_avg:5f}")
    #st.line_chart(tabs)
    wordCloud(df)





















# keywords = {
#     "btc": ["btc","#btc","$btc","bitcoin"],
#     "ada": ["ada","#ada","$ada","cardano"],
#     "eth": ["eth","#eth","$eth","ether","ethereum","etherum"],
#     "bnb": ["bnb","#bnb","$bnb","binance coin"],
#     "xrp": ["xrp","#xrp","$xrp","ripple"],
# }

# @st.cache(allow_output_mutation=True,show_spinner=False)
# def start_stream(keywords):
#     keywords = keywords["btc"]
#     listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3],keywords)
#     listener.filter(track = keywords,languages=["en","de"], threaded= True)
#     print("Stream running...")
#     return listener
    
    
# data, timestamp = get_data()
# col1, col2 = st.columns(2)

# listener = start_stream(keywords)
# st.subheader("Tweet DataFrame")

# update_time = st.slider("Refreshrate (sec):",min_value=10,max_value=5*60,value=10)

# def job():
#     df = pd.DataFrame(data.tail(10))
#     st_avg = float(listener.sent_avg)
#     result_avg = listener.sent_result
#     return df, st_avg , result_avg

# btn = st.button("Refresh")
# if btn: 
#     df, st_avg, result_avg = job()
#     st.dataframe(df)
#     st.write(f"Sentiment Average: {st_avg} = {result_avg}")

