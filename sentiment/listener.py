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
        super().__init__(api_key, api_secret, access_token, access_secret) #Init Twitter API
        init_db() #Init PosgresDB
        self.sentiment_model = SentimentIntensityAnalyzer() # Init Vader SentimentModel
        self.keyword_obj = keyword_obj #Gets Keyword Object 
        self.tweet_list = [] 
        self.amount_filtered = 0

        logging.info(f"Starting Stream for Keywords: {self.keyword_obj.keyword_lst}")

        if self.running:
            self.disconnect()

    def on_status(self, status):
        """Called when Status/Tweet is received
        Args:
            status (Status): Received Status
        """
        sleep(1)
        # Ignore Tweets from Users who only exist for under 60 days. 
        # 60 days = 2 months is pretty high but this really ensures no bots are included (hopefully)
        tz_info = status.user.created_at.tzinfo #gets the timezone 
        diff = datetime.now(tz_info) - status.user.created_at #adding the timezone info to now() so they can be subtracted
        if diff.days < 60:
            logger.info(f"User is only {diff.days} Days on Twitter. Ignored.")
            self.amount_filtered +=1
            return
        
        # Ignores Tweets from User with less than 500 followers 
        if int(status.user.followers_count) < 500:
            logger.info(f"User has only {status.user.followers_count} Followers. Ignored.")
            self.amount_filtered +=1
            return

        # Ignores retweets 
        if status.retweeted or "RT @" in status.text:
            logger.info("Retweet. Ignored.")
            self.amount_filtered +=1
            return
        
        # Gets Text
        if status.truncated:
            text = status.extended_tweet["full_text"]
        else:
            text = status.text
        text = text.lower()
        
        # Checks Text for Blacklisted Words: Giveaway, Free, Gift
        if check_blacklist(text):
            logger.info("Blacklisted Word. Ignored.")
            self.amount_filtered +=1
            return

        # Ignore tweets which do not contain the keyword
        keyword = self.keyword_obj.check_keyword(text)
        if keyword == None:
            print(f"No Keyword in '{text}'. Ignored.")
            self.amount_filtered +=1
            return
        else:
            try:
                #Get Sentiment
                tweet_sentiment = self.sentiment_model.polarity_scores(text).get("compound")
                # Sometimes the Sentiment was faulty and not between -1 and 1. This filters those wrong ones.
                if (tweet_sentiment < -1 or tweet_sentiment > 1):
                    logger.info(f"Sentiment {tweet_sentiment} is a faulty value")
                    self.amount_filtered +=1
                    return
                cleaned_tweet = cleanTweets(text)
                #Adding 2 hours to utc time to match local time (Europe/Berlin)
                status_created_at = status.created_at + timedelta(hours=2)
                user_created_at = status.user.created_at + timedelta(hours=2)
                
                # Adding tweets to a list so they can be checked for duplicates
                metrics = [cleaned_tweet,keyword,status_created_at,status.user.location,status.user.verified,status.user.followers_count,user_created_at,tweet_sentiment]
                self.tweet_list.append(metrics)

                logger.info(f"Collected Tweets: {len(self.tweet_list)}")
                #print(f"Collected Tweets: {len(self.tweet_list)}")
                # There are around 40 Tweets collected in a minute
                # These 40 Tweets will be checked for duplicates and if there are any delete them.
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

                        #Uploading to Heroku Database
                        with session_scope() as sess:
                            #pass
                            sess.add(tweet)
                            time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    print(f"{len(self.tweet_list)} Tweets inserted at {time_now}. Total Tweets filtered: {self.amount_filtered}")
                    self.tweet_list = []
                    self.amount_filtered = 0


            except Exception as e:
                logger.warning(f"Unable to insert tweet: {e}")
        
    # If Twitter API Limit is reached
    def on_limit(self,status):
        print("Rate Limit Exceeded, Sleep for 1 Min")
        sleep(60)
        return True
        
    # Twitter API Error
    def on_error(self,status_code):
        if status_code == 420:
            logger.warning("Streamlimit reached. Closing stream...")
            return False
        logger.warning(f"Streaming error (status code {status_code})")
