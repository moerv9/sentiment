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

rows = st.slider("Rows to retrieve:",step=5,min_value=5,max_value=500)
btn = st.button("Show")
if btn:
    df = get_Heroku_DB(rows)
    st.dataframe(df)