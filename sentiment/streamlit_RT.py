import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os, datetime, logging
from listener import StreamListener
from logging.handlers import RotatingFileHandler

os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment")
from config import ConfigAPI, ConfigDB
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
    layout="wide", 
    page_title="RealTime Tweet Data", 
    )
st.title("RealTime Tweet Data")

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_con():
    return create_engine('postgresql://{}:{}@{}/tweets'.format(ConfigDB.USER, ConfigDB.PASS, ConfigDB.HOST),convert_unicode=True)

def get_data():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df = pd.read_sql_table("tweets",get_con())
    df = df.rename(columns={"body": "Tweet", "tweet_date":"Timestamp", 
        "followers": "Followers", "sentiment": "Sentiment", "keyword": "Keyword",
        "verified_user": "User verified"})
    return df, timestamp

keywords = {
    "btc": ["btc","#btc","$btc","bitcoin"],
    "ada": ["ada","#ada","$ada","cardano"],
    "eth": ["eth","#eth","$eth","ether","ethereum","etherum"],
    "bnb": ["bnb","#bnb","$bnb","binance coin"],
    "xrp": ["xrp","#xrp","$xrp","ripple"],
}



keywords = keywords["btc"]
listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3],keywords)
data, timestamp = get_data()

listener.filter(track = keywords,languages=["en","de"], threaded= True)
print("Stream running...")
col1, col2 = st.columns(2)

col1.subheader("Tweet DataFrame")
col1.dataframe(data.tail(10))

sent_avg = float(listener.sent_avg)


if st.button("Get actual Sentiment"):
    st.text("AVG")
    st.text(str(sent_avg))
    print(f"Avg Sentiment: {sent_avg}")
