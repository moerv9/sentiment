import os, time, logging, schedule
from logging.handlers import RotatingFileHandler
from listener import StreamListener
import pandas as pd
from datetime import datetime,timezone,date

#Config
os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import ConfigAPI
newconf = ConfigAPI()

#Logging
log_dir = 'Logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_name = '{}_stream.log'.format(date.today().strftime('%Y%m%d'))
log_handler = RotatingFileHandler(filename=os.path.join(log_dir, log_name), maxBytes=2000000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                    datefmt='%d-%m-%Y T%H:%M:%S')

def export_to_excel(list):
    columns=["Tweet", "Keyword", "Time", "Location","Verified","Followers","User created", "Sentiment Score", "Sentiment is"]
    pd.set_option("display.max_columns",200)
    df = pd.DataFrame(list, columns = columns)
    df = df.applymap(cleanDates)
    file_name = '{}_stream.xlsx'.format(date.today().strftime('%d-%m-%Y'))
    sheet_name = calc_avg_sentiment(df["Sentiment Score"])
    
    if not os.path.exists(file_name):
        logging.info(f"..created new file: {file_name}")
        df.to_excel(file_name, sheet_name= str(sheet_name))
    else:
        with pd.ExcelWriter(file_name, mode='a', engine="openpyxl",if_sheet_exists="overlay",) as writer:
            df.to_excel(writer, sheet_name=str(sheet_name))
        logging.info(f"...appended to file {file_name} with sheet {sheet_name}")
    
def cleanDates(date):
    if isinstance(date, datetime):

        date = date.astimezone(datetime.now().astimezone().tzinfo)
        #date = date.tz_localize(None)
        date = datetime.strftime(date,"%d-%m-%Y %H:%M")
    return date

def calc_avg_sentiment(sentiment_col):
    sent_avg = sentiment_col.sum() / len(sentiment_col)
    return sent_avg
    
def func():
    tweets = listener.tw_list
    if tweets:
        logging.info(f"...collected {len(tweets)} new Tweets")
        export_to_excel(tweets)
        listener.clean_list()
    

if __name__ == '__main__':
    keywords = ["$btc","#btc","#bitcoin"]
    listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3],keywords)
    logging.info(f"Starting stream: {keywords}")
    print("Stream running...")
    listener.filter(track = keywords, languages=["en","de"], threaded = True)
    
    schedule.every(10).minutes.do(func)

    while True:
        schedule.run_pending()
        time.sleep(1)


