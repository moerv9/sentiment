#Imports
import tweepy
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from time import sleep
from collections import defaultdict
from Tweet_Data.database import init_db, session_scope
from filter import check_blacklist,cleanTweets,check_duplicates
from Tweet_Data.Tweet import Tweet
import pandas as pd

#Config
import sys
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import Config
newconf = Config()
api = newconf.create_api("auth1")

logger = logging.getLogger(__name__)
from sqlalchemy import select,table,column
# %% [markdown]
# ### Class: Real-Time Listener for Tweets
# %%
#TODO: Add my own sentiment analysis -> blob and ML
class StreamListener(tweepy.Stream):
    def __init__(self,api_key, api_secret, access_token, access_secret, keyword_obj):
        super().__init__(api_key, api_secret, access_token, access_secret)
        init_db() #Uncomment when using PosgresDB
        self.sentiment_model = SentimentIntensityAnalyzer()
        self.keyword_obj = keyword_obj
        self.tweet_list = []#defaultdict(list)

        logging.info(f"Starting Stream for Keywords: {self.keyword_obj.keyword_lst}")

        if self.running:
            self.disconnect()

    def on_status(self, status):
        sleep(10)
        """Called when Status/Tweet is received
        Args:
            status (Status): Received Status
        """
        # Ignore Tweets from Users who only exist for under 60 days. 
        # 60 days = 2 months is pretty high but this really ensures no bots are included (hopefully)
        tz_info = status.user.created_at.tzinfo #gets the timezone 
        diff = datetime.now(tz_info) - status.user.created_at #adding the timezone info to now() so they can be subtracted
        if diff.days < 60:
            logger.info(f"User only {diff.days} Days on Twitter. Ignored!")
            return
        
        # Ignores Tweets from User with less than 500 followers 
        if int(status.user.followers_count) < 500:
            logger.info(f"User has only {status.user.followers_count} Followers. Ignored.")
            return

        # Ignores retweets 
        if status.retweeted or "RT @" in status.text:
            logger.info("Ignored retweet")
            return
        
        # Gets Text
        if status.truncated:
            text = status.extended_tweet["full_text"]
        else:
            text = status.text
        text = text.lower()
        
        # Checks Text for Blacklisted Words: Giveaway, Free, Gift
        if check_blacklist(text):
            logger.info("Blacklisted word---")
            return

        #Gets Sentiment
        tweet_sentiment = self.sentiment_model.polarity_scores(text).get("compound")
        if (tweet_sentiment < -1 or tweet_sentiment > 1):
            logger.info(f"Sentiment {tweet_sentiment} is a faulty value")
            return
        # Ignore tweets which do not contain the keyword
        keyword = self.keyword_obj.check_keyword(text)
        if keyword == None:
            return
        else:
            try:
                cleaned_tweet = cleanTweets(text)
                status_created_at = status.created_at + timedelta(hours=2)
                user_created_at = status.user.created_at + timedelta(hours=2)
                
                #Uncomment for local export to json
                metrics = [cleaned_tweet,keyword,status_created_at,status.user.location,status.user.verified,status.user.followers_count,user_created_at,tweet_sentiment]
                
                self.tweet_list.append(metrics)

                logger.info(f"Collected Tweets: {len(self.tweet_list)}")
                # There are around 40 Tweets collected in a minute
                # These 40 Tweets will be checked for duplicates and if there are any delete them.
                # Then insert them into Heroku Database
                if len(self.tweet_list) >=40:
                    cleaned_list = check_duplicates(self.tweet_list)
                    for items in cleaned_list:
                        tweet = Tweet(body = items[0],
                                    keyword = items[1],
                                    tweet_date = items[2],
                                    location = items[3],
                                    verified_user = items[4],
                                    followers = items[5],
                                    user_since = items[6],
                                    sentiment = items[7])
                        # tweet = Tweet(
                        #     body = cleaned_tweet,
                        #     keyword = keyword,
                        #     tweet_date = status_created_at,
                        #     location= str(status.user.location),
                        #     verified_user = status.user.verified, 
                        #     followers = status.user.followers_count,
                        #     user_since = user_created_at, 
                        #     sentiment = tweet_sentiment)
                        with session_scope() as sess:
                            #pass
                            sess.add(tweet)
                    self.tweet_list = []



            except Exception as e:
                logger.warning(f"Unable to insert tweet: {e}")
        
    def on_limit(self,status):
        print("Rate Limit Exceeded, Sleep for 1 Min")
        sleep(60)
        return True

    #Uncomment for local export to json
    #Maybe needed to regularly clean the Expanding list...
    # def clean_dict(self):
    #     self.tweet_dict = []
        
    def on_error(self,status_code):
        if status_code == 420:
            logger.warning("Streamlimit reached. Closing stream...")
            return False
        logger.warning(f"Streaming error (status code {status_code})")
