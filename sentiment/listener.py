#Imports

#import regex
#from config.database import session_scope, init_db
#from config.tweet_data_db import Tweet
import tweepy
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import demoji
from datetime import datetime
from time import sleep
from collections import defaultdict

logger = logging.getLogger(__name__)
# %% [markdown]
# ### Class: Real-Time Listener for Tweets

# %%
#TODO: Add my own sentiment analysis -> blob and ML
class StreamListener(tweepy.Stream):
    def __init__(self,api_key, api_secret, access_token, access_secret, keyword_obj):
        super().__init__(api_key, api_secret, access_token, access_secret)
        #init_db()
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
        keyword, crypto_identifier = self.keyword_obj.check_keyword(text)
        if not keyword:
            return
        
        cleaned_tweet = self.cleanTweets(text)
        metrics = [cleaned_tweet,keyword,status.created_at,status.user.location,status.user.verified,status.user.followers_count,status.user.created_at,tweet_sentiment, tweet_sent_meaning]
        
        try:
            if crypto_identifier:
                self.sum_collected_tweets +=1
                self.tweet_dict[crypto_identifier].append(metrics)
        except:
            raise Exception

        #For Posgres
        # tweet = Tweet(body = cleaned_tweet, keyword= keyword, tweet_date= status.created_at, location= status.user.location,
        #         verified_user= status.user.verified, followers= status.user.followers_count,
        #         user_since= status.user.created_at, sentiment= tweet_sentiment, sentiment_meaning = tweet_sent_meaning)
        # self.insert_tweet(tweet)
        
        
        # self.tweet_lst = self.tweet_lst[:20]
        # if not tweet.body in self.tweet_lst and self.tweet_lst:
        #     self.tweet_lst.insert(0,tweet.body)
        # else:
        #     logger.warning(f"Duplicate Tweet: {tweet.body}")
        #     return

        
    def on_limit(self,status):
        print("Rate Limit Exceeded, Sleep for 1 Min")
        sleep(60)
        return True
    
    # def get_latest_df(self):
    #     df = pd.DataFrame(self.tw_list,columns=["Tweet", "Keyword", "Time", "Location","Verified","Followers","User created", "Sentiment Score", "Sentiment is"])
    #     return df

    def clean_dict(self):
        self.tweet_dict = []
        
    def on_error(self,status_code):
        if status_code == 420:
            logger.warning("Streamlimit reached. Closing stream...")
            return False
        logger.warning(f"Streaming error (status code {status_code})")
        
    # For database connection
    # def insert_tweet(self,tweet):
    #     """Insert Tweet into Database
    #     Args:
    #         tweet (Tweet): Tweet Object
    #     """
    #     try:
    #         with session_scope() as sess:
    #             sess.add(tweet)
    #     except Exception as e:
    #         logger.warning(f"Unable to insert tweet: {e}")
        

    
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

#This whole keyword class could be improved and the check_keyword function from inside on_status should be in here but it works for now
class Keywords():
    def __init__(self,keyword_dict):
        self.keyword_dict = keyword_dict
        
        self.keyword_lst = self.build_keyword_list()
        
    def build_keyword_list(self):
        """Build a list of keywords from a dictionary. Appends the values after the key
        Needed for the Tweet Listener.Filter
        
        Returns:
            list: comma separated list of keywords. 
        """
        new_list = []
        for key, val in self.keyword_dict.items():
            new_list.append(key)
            for i in val:
                new_list.append(i)

        return new_list
        
    def check_keyword(self,body):
        """Check Tweet for keywords

        Args:
            body (String): Tweet Text

        Returns:
            String: returns keyword or None
        """
        i =0 
        for key, val in list(self.keyword_dict.items()):
            # This looks for keyword like "btc" or "ada" -> results in lots of unrelated tweets 
            # if re.search(rf"\b{key}\b", body, re.IGNORECASE):  
            #     return key, list(self.keyword_dict.keys())[i]
            for keyword in val:
                if keyword.lower() in body:
                    return keyword, list(self.keyword_dict.keys())[i]
            #print(f"KEY: {list(self.keyword_dict.keys())[i]}")
            i+=1
        
        return None, None
        