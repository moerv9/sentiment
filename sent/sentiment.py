
## Imports
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import numpy as np
import re
import matplotlib.pyplot as plt
import tweets
plt.style.use("fivethirtyeight")

class Sentiment():
    def __init__(self):
        self.negative_count = 0
        self.positive_count = 0
        self.neutral_count = 0
    
    # Function to get subjectivity
    def getSubjectivity(self,text):
        subj = TextBlob(text).sentiment.subjectivity
        return int(subj * 100)

    # Function to get polarity (how positiv or negative)
    def getPolarity(self,text):
        pol = TextBlob(text).sentiment.polarity
        if pol < 0:
            self.negative_count += 1
            return "Negative"
        elif pol == 0:
            self.neutral_count += 1
            return "Neutral"
        else:
            self.positive_count += 1
            return "Positive"