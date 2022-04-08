# Import Twitter API TOKEN
from config import ConfigAPI
newconf = ConfigAPI()
api = newconf.create_api("auth1")

## Imports
import tweepy
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import numpy as np
import re
import matplotlib.pyplot as plt
import tweets
plt.style.use("fivethirtyeight")

class Sentiment():
    
    # Function to get subjectivity
    def getSubjectivity(self,text):
        subj = TextBlob(text).sentiment.subjectivity
        return int(subj * 100)

    # Function to get polarity (how positiv or negative)
    def getPolarity(self,text):
        pol = TextBlob(text).sentiment.polarity
        if pol < 0:
            return "Negative"
        elif pol == 0:
            return "Neutral"
        else:
            return "Positive"
    