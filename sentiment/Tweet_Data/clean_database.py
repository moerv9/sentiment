from datetime import timedelta
import schedule,time,logging,os
import psycopg2
import pandas as pd
#Logging
logger = logging.getLogger(__name__)
# Config
os.sys.path.insert(0, "/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigDB
DB_URL = ConfigDB().DB_URL

def repeat_func():
    conn = psycopg2.connect(DB_URL,sslmode="require")
    query = f"select * from tweet_data where Tweet_Date < (current_date - Integer '1') order by id desc;"
    df = pd.read_sql(query,conn)
    columns = {"body": "Tweet",
                "keyword": "Keyword",
                "tweet_date": "Timestamp",
                "location": "Location",
                "verified_user": "User verified",
                "followers": "Followers",
                "user_since": "User created",
                "sentiment": "Sentiment Score",
                "sentiment_meaning": "Null"}
    df = df.drop(columns=["sentiment_meaning"])
    df = df.rename(columns=columns)
    df["Timestamp"] = df["Timestamp"] + timedelta(hours=2)
    print(df.head(5))

#Method for schedule task execution
def schedule(interval=5):
        schedule.every(interval).minutes.do(repeat_func)
        while True:
            schedule.run_pending()
            time.sleep(1)