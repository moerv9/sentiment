from datetime import datetime, time
import logging
import re
import demoji
from dateutil import tz
import pandas as pd

logger = logging.getLogger(__name__)
    
def check_blacklist(body):
    """Check Tweet for forbidden Words like "Giveaway"
    Args:
        body (String): Tweet Text
    Returns:
        bool: True if body contains blacklisted word
    """
    blacklist = ["giveaway","free","gift"]
    for word in blacklist:
        if word in body:
            #logger.info(f"Blacklisted word: {word}, Removed Tweet: {body}")
            return True
        
def cleanTweets(text):
    """Removes unnecessary information from tweets
    Args:
        text (str): input text
    Returns:
        str: cleaned text
    """
    text = re.sub(r'@[A-Za-z0-9]+',"",text,flags=re.IGNORECASE) #removes @mentions / r tells python that it is a raw stream (regex)
    #text = re.sub(r'#[A-Za-z0-9]+',"",text, flags=re.IGNORECASE) #removes # 
    text = re.sub(r':',"",text,) #removes ':'
    text = demoji.replace(text, "") #removes emojis
    text = re.sub(r'\n+',"",text) #removes \n 
    text = re.sub(r'&amp;*|&amp|amp',"",text) #removes &amp;
    text = re.sub(r'RT[\s]+',"",text) #removes retweets
    text = re.sub(r'_*|\+*',"",text) # removes _ and +
    text = re.sub(r"\.|\!|\,|\(|\)|\-|\?|\;|\\|\'","",text) #removes other symbols
    #text = re.sub(r'https?:\/\/\S+',"",text) #removes hyperlink, the '?' matches 0 or 1 reps of the preceding 's'
    text = re.sub(r"http\S+","",text,flags=re.IGNORECASE)
    words = text.split(" ")
    cleaned_words = [x for x in words if not bool(re.search('^[0-9]+$|^$', x))]#removes empty string ("") and numbers that stand alone like 981238 but leaves numbers with symbols or letters like $50k
    text = " ".join(cleaned_words)
    return text


def check_duplicates(tweet_list):
    cols = ["Tweet", "Keyword", "Time", "Location","Verified","Followers","User created", "Sentiment Score"]
    df = pd.DataFrame(tweet_list,columns=cols)
    duplicates = list(df.index[df.duplicated(subset=["Tweet"],keep=False)])
    df.drop(labels=duplicates,inplace=True)
    logger.info(f"Deleted {len(duplicates)} duplicates.")
    print(f"Deleted {len(duplicates)} duplicates.")
    return df.values.tolist()