import os, time, logging, schedule
#from listener import StreamListener, Keywords
import pandas as pd
from datetime import datetime,timezone,date
from runner import StartListener
import json

#Config
#os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config_sent import ConfigAPI
newconf = ConfigAPI()

#Logging
logger = logging.getLogger(__name__)

class Export():
    def __init__(self):
        self.columns=["Tweet", "Keyword", "Time", "Location","Verified","Followers","User created", "Sentiment Score", "Sentiment is"]
        pass
    
    def export_to_excel(self,list):
        #pd.set_option("display.max_columns",200)
        df = pd.DataFrame(list, columns = self.columns)
        df = df.applymap(self.cleanDates)
        
        excel_dir = 'Excel_Logs'
        if not os.path.exists(excel_dir):
            os.mkdir(excel_dir)
        
        excel_file = '{}_stream.xlsx'.format(date.today().strftime('%d-%m-%Y'))
        file_name = os.path.join(excel_dir,excel_file)
        sheet_name = self.calc_avg_sentiment(df["Sentiment Score"])
        
        if not os.path.exists(file_name):
            logging.info(f"..created new file: {file_name}")
            df.to_excel(file_name, sheet_name= str(sheet_name))
        else:
            with pd.ExcelWriter(file_name, mode='a', engine="openpyxl",if_sheet_exists="overlay",) as writer:
                df.to_excel(writer, sheet_name=str(sheet_name))
            logging.info(f"...appended to file {file_name} with sheet {sheet_name}")
            
        
    def cleanDates(self,date):
        """Mandatory for Excel. Converts date to local timeformat.

        Args:
            date (_type_): date

        Returns:
            date: astimezone and seconds stripped
        """
        if isinstance(date, datetime):

            date = date.astimezone(datetime.now().astimezone().tzinfo)
            #date = date.tz_localize(None)
            date = datetime.strftime(date,"%d-%m-%Y %H:%M")
        return date
    
    def export_to_json(self):
        json_dir = 'sentiment/Json'
        if not os.path.exists(json_dir):
            os.mkdir(json_dir)
            
        for key, val in list(self.tweet_dict.items()):
            json_file = os.path.join(json_dir,f"{key}.json")
            df_to_append = pd.DataFrame(val, columns = self.columns)
            df_to_append = df_to_append.applymap(self.cleanDates)
            if os.path.isfile(json_file):
                df_read = pd.read_json(json_file,orient="index")
                df_read = pd.concat([df_read,df_to_append],ignore_index=True)
                df_read.drop_duplicates(inplace=True)
                df_read.to_json(json_file,orient="index",indent=4)
            else:
                df_to_append.to_json(json_file,orient="index",indent=4) #records= kein Index,

    def calc_avg_sentiment(self,sentiment_col):
        sent_avg = sentiment_col.sum() / len(sentiment_col)
        return sent_avg
        
    def func(self):
        self.tweet_dict = listener.tweet_dict
        if self.tweet_dict:
            logging.info(f"{listener.sum_collected_tweets} Tweets collected")
            # export_to_excel(tweets)
            self.export_to_json()
            # listener.clean_list()
        


if __name__ == '__main__':
    listener = StartListener().run()
    export = Export()
    schedule.every(0.1).minutes.do(export.func)

    while True:
        schedule.run_pending()
        time.sleep(1)
