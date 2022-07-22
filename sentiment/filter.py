from datetime import datetime, time
import re
import demoji
from dateutil import tz



    
def check_blacklist(body):
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
        
def cleanTweets(text):
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

def datetime_from_utc_to_local(utc_datetime):
    # Get local timezone
    local_zone = tz.tzlocal()
    # Convert UTC to local time zone
    local_dt = utc_datetime.astimezone(local_zone)
    return local_dt