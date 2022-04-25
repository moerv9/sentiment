#Imports
import sys
from database import session_scope, init_db
from tweet_metrics import Tweet
import tweepy
import logging
import pandas as pd 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import demoji
from datetime import datetime
from time import sleep


#Config
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigAPI
newconf = ConfigAPI()
api = newconf.create_api("auth1")


logger = logging.getLogger(__name__)
# %% [markdown]
# ### Class: Real-Time Listener for Tweets

# %%
#TODO: Add my own sentiment analysis -> blob and ML
class StreamListener(tweepy.Stream):
    def __init__(self,api_key, api_secret, access_token, access_secret, keywords):
        super().__init__(api_key, api_secret, access_token, access_secret)
        init_db()
        self.keywords = keywords
        self.sentiment_model = SentimentIntensityAnalyzer()
        self.tw_list = []
        
        if self.running:
            self.disconnect()

    def on_status(self, status):
        sleep(0.1)
        """Called when Status/Tweet is received
        Args:
            status (Status): Received Status
        """
        # Ignore Tweets from Users who only exist for under 60 days. 
        # 60 days = 2 months is pretty high but this really ensures no bots are included (hopefully)
        tz_info = status.user.created_at.tzinfo #gets the timezone 
        diff = datetime.now(tz_info) - status.user.created_at #adding the timezone info to now() so they can be subtracted
        if diff.days < 60:
            #logger.info(f"User only {diff.days} Days on Twitter. Ignored!")
            return
        
        # Ingores retweets
        if status.retweeted or "RT @" in status.text:
            return
        
        # Gets Text
        if status.truncated:
            text = status.extended_tweet["full_text"]
        else:
            text = status.text
        text = text.lower()
        
        # Ignores Tweets with forbidden words 
        if self.check_blacklist(text):
            return
            
        location = status.user.location
        if location:
            location = str(status.user.location)
            
        tweet_sentiment = self.sentiment_model.polarity_scores(text).get("compound")
        if tweet_sentiment > 0.1:
            tweet_sent_meaning = "Positive"
        elif tweet_sentiment< -0.1:
            tweet_sent_meaning =  "Negative"
        else:
            tweet_sent_meaning = "Neutral"
        
        # Ignore tweets which do not contain the keyword
        keyword = self.check_keyword(text)
        if not keyword:
            return

        cleaned_tweet = self.cleanTweets(text)
        '''tweet = Tweet(body = cleaned_tweet, keyword= keyword, tweet_date= status.created_at, location= status.user.location,
                    verified_user= status.user.verified, followers= status.user.followers_count,
                    user_since= status.user.created_at, sentiment= tweet_sentiment, sentiment_meaning = tweet_sent_meaning)
        '''
        
        # self.tweet_lst = self.tweet_lst[:20]
        # if not tweet.body in self.tweet_lst and self.tweet_lst:
        #     self.tweet_lst.insert(0,tweet.body)
        # else:
        #     logger.warning(f"Duplicate Tweet: {tweet.body}")
        #     return
        
        self.tw_list.append([cleaned_tweet,keyword,status.created_at,status.user.location,status.user.verified,status.user.followers_count,status.user.created_at,tweet_sentiment, tweet_sent_meaning])
        
        #self.insert_tweet(tweet)
        
    def on_limit(self,status):
        print("Rate Limit Exceeded, Sleep for 1 Min")
        sleep(60)
        return True
    
    def get_latest_df(self):
        df = pd.DataFrame(self.tw_list,columns=["Tweet", "Keyword", "Time", "Location","Verified","Followers","User created", "Sentiment Score", "Sentiment is"])
        return df

    def clean_list(self):
        self.tw_list = []

        #logger.info(f"Avg Sentiment Log: {self.sent_avg}")
        
    def on_error(self,status_code):
        if status_code == 420:
            logger.warning("Streamlimit reached. Closing stream...")
            return False
        logger.warning(f"Streaming error (status code {status_code})")
        
    
    def insert_tweet(self,tweet):
        """Insert Tweet into Database
        Args:
            tweet (Tweet): Tweet Object
        """
        try:
            with session_scope() as sess:
                sess.add(tweet)
        except Exception as e:
            logger.warning(f"Unable to insert tweet: {e}")
        
    def check_keyword(self,body):
        """Check Tweet for keywords

        Args:
            body (String): Tweet Text

        Returns:
            String: returns keyword or None
        """
        
        if re.search(rf"\b{self.keywords[0]}\b", body, re.IGNORECASE):
            return self.keywords[0]
        
        for keyword in self.keywords[1:]:
            if keyword.lower() in body:
                return keyword
        return None
    
    def check_blacklist(self, body):
        """Check Tweet for forbidden Words like "Giveaway"

        Args:
            body (String): Tweet Text

        Returns:
            bool: True if body contains blacklisted word
        """
        blacklist = ["giveaway","free"]
        for word in blacklist:
            if word in body:
                #logger.info(f"Blacklisted word: {word}, Removed Tweet: {body}")
                return True
            
    
    def cleanTweets(self, text):
        """Removes unnecessary information from tweets
        Args:
            text (str): input text
        Returns:
            str: cleaned text
        """
        text = re.sub(r'@[A-Za-z0-9]+',"",text,flags=re.IGNORECASE) #removes @mentions / r tells python that it is a raw stream (regex)
        text = re.sub(r'#[A-Za-z0-9]+',"",text, flags=re.IGNORECASE) #removes # 
        text = re.sub(r':',"",text,) #removes ':'
        text = demoji.replace(text, "") #removes emojis
        text = re.sub(r'\n+',"",text) #removes \n 
        text = re.sub(r'&amp;+',"",text) #removes &amp;
        text = re.sub(r'RT[\s]+',"",text) #removes retweets
        #text = re.sub(r'https?:\/\/\S+',"",text) #removes hyperlink, the '?' matches 0 or 1 reps of the preceding 's'
        text = re.sub(r"http\S+","",text,flags=re.IGNORECASE)
        return text
