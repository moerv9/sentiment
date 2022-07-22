from datetime import date
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB,get_mean_Sentiment
import matplotlib.pyplot as plt
import altair as alt

##PAGE SETUP
logger = logging.getLogger(__name__)
st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader(f"Twitter Sentiment-Streaming for {date.today().strftime('%d-%m-%Y')}")

df = get_Heroku_DB()
#st.dataframe(df)

df_mean_byMinute = get_mean_Sentiment(df)
#st.dataframe(df_mean_byMinute)


fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlabel("Timestamp")
ax.set_ylabel("Sentiment Score")
ax.set_xlim(auto=True)
#ax.xaxis.label.set_size(5)
ax.plot(df_mean_byMinute)
#plt.gcf().autofmt_xdate()
plt.tick_params('x')   
plt.tight_layout()
st.pyplot(fig)

#st.line_chart(df_mean_byMinute)
#filtered_df= df.query("tweet_date == bitcoin or tweet_date == #btc")
#st.dataframe(filtered_df)
#mean_df= df.query("tweet_date == bitcoin or tweet_date == #btc")['sentiment'].mean()
#st.text(f"Sentiment Mean: {mean_df}")
