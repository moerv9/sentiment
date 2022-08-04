from datetime import date
import os, logging
import streamlit as st
from streamlit_data import get_Heroku_DB
##PAGE SETUP
logger = logging.getLogger(__name__)
st.set_page_config(
    page_title="Sentiment", 
    layout="wide", 
    )
st.subheader("Datasets")

@st.cache(ttl=60*5)
def loading_data_from_heroku_database():
    return get_Heroku_DB()

rows = st.slider("Rows to retrieve:",step=5,min_value=5,max_value=500,value=5)
btn = st.button("Refresh Database")
if btn:
    loading_data_from_heroku_database()
    
df = loading_data_from_heroku_database()

btc_df = df[df["Keyword"].isin(["#btc","$btc","bitcoin"])]


st.subheader("Bitcoin")
st.dataframe(btc_df.head(rows))

def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')

csv = convert_df(df.head(5))

st.download_button(
     label="Download data as CSV",
     data=csv,
     file_name='btcdf.csv',
     mime='text/csv',
 )