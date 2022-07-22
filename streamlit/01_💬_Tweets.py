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
st.subheader(f"Twitter Sentiment-Streaming for {date.today().strftime('%d-%m-%Y')}")

df = get_Heroku_DB()

