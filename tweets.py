# %% [markdown]
# ## Classes

# %% [markdown]
# ### Import Twitter Token

# %%
# Import Twitter API TOKEN
# import logging
# import sys
# sys.path.append('../../')

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger()
from matplotlib.pyplot import hist
from config import ConfigAPI
newconf = ConfigAPI()
api = newconf.create_api("auth1")

# %% [markdown]
# ### Class: List to Dataframe & export as Excel or Json

# %%
import tweepy
import pandas as pd        

class ListToDF():
    """Converts a list to pandas Dataframe
    
    Args: 
        list (list): data
        columns (list): Title of Columns 
    -------
    Methods:
        export(type="Json" or "Excel, file_name="NameOfFile"): exports the Dataframe
        
        cleanDates(date=date): makes the date timezone unware so it can be exported to excel
    """
    columns = ["Tweet", "Timestamp of Tweet", "Retweets", "Following", "Verified", "User created"]
    
    def __init__(self,list):
        pd.set_option("display.max_columns",100)

        self.df = pd.DataFrame(list,columns = self.columns)
        
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
        import datetime
        self.date=date
        if isinstance(self.date,datetime.datetime):
            self.date = self.date.tz_localize(None)
            self.date = datetime.datetime.strftime(date,"%d-%m-%Y %H:%M")
        return self.date

#TODO: Export this to a new File called DataHandling.py 


# %% [markdown]
# ### Class: Real-Time Listener for Tweets

# %%

class StreamListener(tweepy.Stream):
    """Init Streamlistener

        Args:
            limit (int, optional): Limit of Tweets to be returned. Defaults to None.
        """
    def __init__(self,api_key, api_secret, access_token, access_secret, limit:int = None):
        super().__init__(api_key, api_secret, access_token, access_secret)
        self.tweets = []
        if limit:
            self.limit= limit
        else:
            self.limit = 10
    
    def on_status(self, status):
        self.tweets.append(status)
        
        if len(self.tweets) == self.limit:
            self.disconnect()
        
    def on_error(self,status):
        print(status)

class SearchStream():
    listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3])
        
    def filter_by_keywords(self,keywords:list):
        """Filter Twitter Stream by Keywords

        Args:
            keywords (list): Filter by list of keywords

        Returns:
            data (list): List of Tweets
        """
        self.listener.filter(track = keywords,languages=["en"])
        data = []
        for tweet in self.listener.tweets:
            if not tweet.truncated:
                data.append([tweet.text, tweet.created_at, tweet.retweet_count, tweet.user.followers_count, tweet.user.verified, tweet.user.created_at])
            else:
                data.append([tweet.extended_tweet, tweet.created_at, tweet.retweet_count, tweet.user.followers_count, tweet.user.verified, tweet.user.created_at])
        return data
    
    



# %% [markdown]
# ### Test: Get Realtime Tweets, filter and export to Dataframe & Excel

# %%
#if __name__ == "main":
# columns=["Tweet", "Timestamp of Tweet", "Retweets", "Following", "Verified", "User created"]

# # Initalise a new Object of SearchKeywordsInStream and call the function filter_by_keywords
# kws = SearchStream().filter_by_keywords(["btc", "#btc"])

# # Creating a new Object from ListToDF and add the list kws and columns as Args
# df = ListToDF(kws, columns=columns)

# # Exporting this list to Excel with filename 'exported_DataFrame.xlsx'
# df.export()

# # Print out the DataFrame
# df.df



# %% [markdown]
# ### Class: History from Tweets

# %%

#TODO: Extract Twitter history, 30days or max. days? or other day input and add to list
class SearchTwitterHistory():
    def __init__(self):
        pass
    
    def filter_by_keywords(self, kind_of_search:str="search_tweets", keywords:list=[""], return_count:int=10):
        """_summary_

        Args:
            kind_of_search (str, optional): Searches max. 7 days of tweets. Defaults to "search_tweets".
            keywords (list, optional): _description_. Defaults to [""].
            return_count (int, optional): _description_. Defaults to 10.

        Returns:
            _type_: _description_
        """
        data = []
        if kind_of_search == "search_tweets" or None:
            for tweet in tweepy.Cursor(api.search_tweets, result_type="popular", tweet_mode="extended",q=keywords,lang="en").items(return_count):
                data.append([tweet.full_text, tweet.created_at,tweet.retweet_count, tweet.user.followers_count, tweet.user.verified, tweet.user.created_at])
        return data
        

# %% [markdown]
# ### Test: Tweet History
# 

# %%
#if __name__ == "main":
# columns=["Tweet", "Timestamp of Tweet", "Retweets", "Following", "Verified", "User created"]
# keywords=["btc","#btc","$btc"]
# history_search= SearchTwitterHistory().filter_by_keywords("search_tweets",keywords,15)
# df= ListToDF(history_search,columns=columns)
# df.df



### Test: ListToDF
history_search= SearchTwitterHistory().filter_by_keywords("search_tweets",["btc","#btc"],5)

#list = ["test1","test2","test3","test4","test5","test6"]
newList = ListToDF(history_search)
print(newList.df.to_string())