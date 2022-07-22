#Imports
import tweepy
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
from time import sleep
from collections import defaultdict
from filter import check_blacklist,cleanTweets,datetime_from_utc_to_local
from Tweet_Data.database import session_scope, init_db #Uncomment when using PosgresDB
from Tweet_Data.Tweet import Tweet #Uncomment when using PosgresDB
from keywords import Keywords
logger = logging.getLogger(__name__)
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
        self.tweet_dict = defaultdict(list)
        logging.info(f"Starting stream: {self.keyword_obj.keyword_lst}")
        self.sum_collected_tweets = 0

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

        # Ignores retweets 
        # Ignores Tweets with forbidden words 
        if status.retweeted or "RT @" in status.text:
            return
        
        # Gets Text
        if status.truncated:
            text = status.extended_tweet["full_text"]
        else:
            text = status.text
        text = text.lower()
        
        if check_blacklist(text):
            return

        #Gets Sentiment
        tweet_sentiment = self.sentiment_model.polarity_scores(text).get("compound")
        # Ignore tweets which do not contain the keyword
        keyword = self.keyword_obj.check_keyword(text)
        if keyword == None:
            return
        else:
            try:
                self.sum_collected_tweets +=1
                cleaned_tweet = cleanTweets(text)
                status_created_at = datetime_from_utc_to_local(status.created_at)  
                user_created_at = datetime_from_utc_to_local(status.user.created_at)
                #Uncomment for local export to json
                #metrics = [cleaned_tweet,keyword,status.created_at,status.user.location,status.user.verified,status.user.followers_count,status.user.created_at,tweet_sentiment]
                #self.tweet_dict[crypto_identifier].append(metrics)
                
                #Uncomment when using PosgresDB
                tweet = Tweet(body = cleaned_tweet, keyword= keyword, tweet_date= status_created_at, location= str(status.user.location),
                        verified_user= status.user.verified, followers= status.user.followers_count,
                        user_since= user_created_at, sentiment= tweet_sentiment)
                with session_scope() as sess:
                    sess.add(tweet)

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
