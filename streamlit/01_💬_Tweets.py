from datetime import date
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB,get_mean_Sentiment
import matplotlib.pyplot as plt
import altair as alt
from matplotlib.ticker import (MultipleLocator,
                            FormatStrFormatter,
                            AutoMinorLocator)

##PAGE SETUP
logger = logging.getLogger(__name__)
st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader(f"Twitter Sentiment-Streaming for {date.today().strftime('%d-%m-%Y')}")

@st.cache()
def get_db():
    return get_Heroku_DB()
#st.dataframe(df)

df = get_db()

df_mean_byMinute, day = get_mean_Sentiment(df.head(3000))
#st.dataframe(df_mean_byMinute)


fig, ax = plt.subplots(figsize=(12, 6))
ax.set_title(day)
ax.set_xlabel("Time")
ax.set_ylabel("Sentiment Score")
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.xaxis.set_minor_locator(MultipleLocator(5))
ax.set_xlim(auto=True)
ax.xaxis.label.set_size(20)
ax.plot(df_mean_byMinute)
plt.gcf().autofmt_xdate()
#plt.tick_params('x')   
plt.tight_layout()
st.pyplot(fig)



#st.line_chart(df_mean_byMinute)
#filtered_df= df.query("tweet_date == bitcoin or tweet_date == #btc")
#st.dataframe(filtered_df)
#mean_df= df.query("tweet_date == bitcoin or tweet_date == #btc")['sentiment'].mean()
#st.text(f"Sentiment Mean: {mean_df}")
