import os, time, logging, schedule
import pandas as pd
from datetime import datetime,timezone,date

#Config
#os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import Config
newconf = Config()

#Logging
logger = logging.getLogger(__name__)

class Export():
    def __init__(self,listener,interval):
        self.columns=["Tweet", "Keyword", "Time", "Location","Verified","Followers","User created", "Sentiment Score", "Sentiment is"]
        print("Exporter initiated...")
        logger.info("Exporter initiated...")
        self.listener = listener
        self.schedule(interval)
        
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
        #Changed this to "sentiment/Json" for heroku. normally would just say "Json" -> could catch that
        json_dir = 'sentiment/Json/'
        date_dir = date.today().strftime('%d-%m-%Y')
        final_dir = os.path.join(json_dir,date_dir)
        if not os.path.exists(final_dir):
            os.mkdir(final_dir)
            print(f"Created new Directory for {date_dir}")
            logger.info(f"Created new Directory for {date_dir}")
            
        for key, val in list(self.tweet_dict.items()):
            json_file = os.path.join(final_dir,f"{key}.json")
            df_to_append = pd.DataFrame(val, columns = self.columns)
            df_to_append = df_to_append.applymap(self.cleanDates)
            if os.path.isfile(json_file):
                df_read = pd.read_json(json_file,orient="index")
                df_read = pd.concat([df_read,df_to_append],ignore_index=True)
                df_read.drop_duplicates(inplace=True)
                df_read.to_json(json_file,orient="index",indent=4,force_ascii=False)
            else:
                df_to_append.to_json(json_file,orient="index",indent=4) #records= kein Index,


    #The function exporting to json will be repeated in the schedule 
    def repeat_func(self):
        self.tweet_dict = self.listener.tweet_dict
        if self.tweet_dict:
            logger.info(f"{self.listener.sum_collected_tweets} Tweets collected")
            # export_to_excel(tweets)
            self.export_to_json()
            # listener.clean_list()
        
    #Method for schedule task execution
    def schedule(self,interval=5):
            schedule.every(interval).minutes.do(self.repeat_func)
            while True:
                schedule.run_pending()
                time.sleep(1)




    # def export_to_excel(self,list):
    #     #pd.set_option("display.max_columns",200)
    #     df = pd.DataFrame(list, columns = self.columns)
    #     df = df.applymap(self.cleanDates)
        
    #     excel_dir = 'Excel_Logs'
    #     if not os.path.exists(excel_dir):
    #         os.mkdir(excel_dir)
        
    #     excel_file = '{}_stream.xlsx'.format(date.today().strftime('%d-%m-%Y'))
    #     file_name = os.path.join(excel_dir,excel_file)
    #     sheet_name = calc_avg_sentiment(df["Sentiment Score"])
        
    #     if not os.path.exists(file_name):
    #         logging.info(f"..created new file: {file_name}")
    #         df.to_excel(file_name, sheet_name= str(sheet_name))
    #     else:
    #         with pd.ExcelWriter(file_name, mode='a', engine="openpyxl",if_sheet_exists="overlay",) as writer:
    #             df.to_excel(writer, sheet_name=str(sheet_name))
    #         logging.info(f"...appended to file {file_name} with sheet {sheet_name}")
            
    #         # Used to calculate the avg sentiment to save as excel sheetname
    #     def calc_avg_sentiment(sentiment_col):
    #         sent_avg = sentiment_col.sum() / len(sentiment_col)
    #         return sent_avg  