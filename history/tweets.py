# %% [markdown]
# ## Classes

# %% [markdown]
# ### Import Twitter Token

# %%
import sys
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p: ', filename="tweet_logs.log",level=logging.INFO)
log = logging.getLogger()

# Import Twitter API TOKEN
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from streamlit.config import ConfigAPI
newconf = ConfigAPI()
api = newconf.create_api("auth1")

# %% [markdown]
# ### Class: List to Dataframe & export as Excel or Json

# %%
import tweepy
import pandas as pd
import datetime
import re
import demoji

class TweetManipulation():
    """Converts a list to pandas Dataframe

    Args:
        list (list): data
        columns (list): Title of Columns
    -------
    Methods:
        export(type="Json" or "Excel, file_name="NameOfFile"): exports the Dataframe

        cleanDates(date=date): makes the date timezone unware so it can be exported to excel
    """
    def __init__(self):
        self.columns = ["Tweet", "Timestamp of Tweet", "Retweets", "Following", "Verified", "User created"]
        self.word_blacklist = set(["giveaway","nft"])

    def listToDataFrame(self,list):
        pd.set_option("display.max_columns",200)
        self.df = pd.DataFrame(list, columns = self.columns)
        self.df = self.df.applymap(self.cleanDates)
        self.df["Tweet"] = self.df["Tweet"].apply(lambda a: self.cleanTweets(a)) 
        #self.df["Tweet"] = self.df["Tweet"].apply(lambda a: self.checkBlacklist(a))      
        return self.df

    def export(self,type="Excel",file_name="exported_DataFrame"):
        """exports the Dataframe to Json or Excel

        Args:
            type (str, "Excel" or "Json"): Export to Excel or Json. Defaults to Excel.
            file_name (str, optional): Filename as String. Extension, .json or .xlsx, will be added automatically. Defaults to "exported_DataFrame".
        """
        if type=="Json":
            self.file_name = file_name + ".json"
            self.df.to_json(self.file_name)
        elif type == "Excel":
            self.df = self.df.applymap(self.cleanDates)
            self.file_name = file_name +".xlsx"
            self.df.to_excel(self.file_name)

    def cleanDates(self,date):
        """Cleans the Datetime Format by making it timezone unaware so it can be exported to Excel

        Args:
            date (str or datatime): Input. Use in .apply or .applymap for pandas Dataframes

        Returns:
            date: Returns cleaned date
        """
        self.date=date
        if isinstance(self.date,datetime.datetime):
            self.date = self.date.tz_localize(None)
            self.date = datetime.datetime.strftime(date,"%d-%m-%Y %H:%M")
        return self.date
    
    def cleanTweets(self, text):
        """Removes unnecessary information from tweets

        Args:
            text (str): input text

        Returns:
            str: cleaned text
        """
        text = re.sub(r'@[A-Za-z0-9]+','',text) #removes @mentions / r tells python that it is a raw stream (regex)
        #text = re.sub(r'#+','',text) #removes # 
        text = re.sub(r':',"",text) #removes ':'
        text = demoji.replace(text, "") #removes emojis
        text = re.sub(r'\n+','',text) #removes \n 
        text = re.sub(r'&amp;+','',text) #removes &amp;
        text = re.sub(r'RT[\s]+','',text) #removes retweets
        text = re.sub(r'https?:\/\/\S+','',text) #removes hyperlink, the '?' matches 0 or 1 reps of the preceding 's'
        
        return text
    
"""
#TODO: not working yet
def checkBlacklist(self, text):
        Checks the pandas column for forbidden or not relevant words and drops the row

        Args:
            text (_type_): _description_

        Returns:
            str: text
        
        #ind_drop = df[df['Tweet'].apply(lambda x: x.startswith('Keyword'))].index
        split_text = set(text.split())
        # ind_drop = self.df[self.df['Tweet'].apply(lambda x: True if self.word_blacklist in x.split() else False)].index
        # log.info(ind_drop)
        if self.word_blacklist.intersection(split_text):
            log.info(self.df["Tweet"])
            idx = self.df["Tweet"].index
            log.info(f"Dropped row {idx} for containing blacklist word: " +str(text))
            self.df["Tweet"].drop(idx,inplace=True)
        return " ".join(split_text)

    def checkDuplicates(self):
        dupl_rows = self.df.duplicated(subset="Tweet")
        return dupl_rows
"""



# %% [markdown]
# ### Class: History from Tweets

# %%

#TODO: Extract Twitter history, 30days or max. days? or other day input and add to list
class SearchTwitterHistory():
    def __init__(self):
        pass

    def filter_by_keywords(self, kind_of_search:str="search_tweets", result_type:str="popular", keywords:list=[""], return_count:int=10):
        """_summary_

        Args:
            kind_of_search (str, optional): Searches max. 7 days of tweets. Defaults to "search_tweets".
            result_Type (str, optional): Type of Result: popular, mixed or recent. Defaults to popular
            keywords (list, optional): _description_. Defaults to [""].
            return_count (int, optional): _description_. Defaults to 10.

        Returns:
            _type_: _description_
        """
        data = []
        if kind_of_search == "search_tweets" or None:
            for tweet in tweepy.Cursor(api.search_tweets, result_type=result_type, tweet_mode="extended",q=keywords,lang="en").items(return_count):
                data.append([tweet.full_text, tweet.created_at,tweet.retweet_count, tweet.user.followers_count, tweet.user.verified, tweet.user.created_at])
        elif kind_of_search == "search_30_day":
            print("30DAYS")
            for tweet in tweepy.Cursor(api.search_30_day, result_type=result_type, tweet_mode="extended",q=keywords,lang="en").items(return_count):
                data.append([tweet.full_text, tweet.created_at,tweet.retweet_count, tweet.user.followers_count, tweet.user.verified, tweet.user.created_at])
        elif kind_of_search == "search_full_archive":
            for tweet in tweepy.Cursor(api.search_full_archive, result_type=result_type, tweet_mode="extended",q=keywords,lang="en").items(return_count):
                    data.append([tweet.full_text, tweet.created_at,tweet.retweet_count, tweet.user.followers_count, tweet.user.verified, tweet.user.created_at])
        return data


# %% [markdown]
# ### Test: Tweet History
#

# %%
#if __name__ == "main":
# columns=["Tweet", "Timestamp of Tweet", "Retweets", "Following", "Verified", "User created"]
# keywords=["btc","#btc","$btc"]
# history_search= SearchTwitterHistory().filter_by_keywords("search_tweetsª",keywords,15)
# df= TweetManipulation.listToDataFrame(history_search,columns=columns)
# df.df


# %% 
### Test: ListToDF
# history_list= SearchTwitterHistory().filter_by_keywords("search_tweets","mixed",["btc","#btc"],200)
# tm = TweetManipulation()
# df = tm.listToDataFrame(history_list)

# df["duplicate"]=tm.checkDuplicates()