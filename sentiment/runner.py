#!/usr/bin/env python
import os, logging, argparse
from logging.handlers import RotatingFileHandler
from listener import StreamListener, Keywords
from datetime import datetime,date, time 
from IPython.display import display
import pandas as pd
from exporter import Export

log_dir = 'Logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_name = '{}_stream.log'.format(date.today().strftime('%Y%m%d'))
log_handler = RotatingFileHandler(filename=os.path.join(log_dir, log_name), maxBytes=2000000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                    datefmt='%d-%m-%Y T%H:%M:%S')
logger = logging.getLogger(__name__)

#Config
#os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import Config
newconf = Config()


logger = logging.getLogger(__name__)

default_keyword_dict ={
                "btc":["#btc","$btc","bitcoin"],
                "ada":["#ada","$ada","cardano"],
                "eth":["#eth","$eth","ether","ethereum","etherum"],
                "bnb":["#bnb","$bnb","binance coin"],
                "xrp":["#xrp","$xrp","ripple"],
}

class Runner():
    def __init__(self,keyword_dict=None,export_interval=10):
        """The Runner starts the listener & exporter with given keyword dictionary

        Args:
            keyword_dict (dict, optional): Dictonairy for Keyowrds.             
            Format for dict:
                dict = {
                    "btc":["#btc","$btc"],
                    "ada":["#ada","$ada"],}
                Defaults to None.
            export_interval (int, optional): Exporting the Data to Json every Interval. Defaults to 10. In Minutes.
        """
        self.keyword_dict = {}
        if keyword_dict is None: 
            self.keyword_dict = default_keyword_dict
        else:
            if isinstance(keyword_dict, dict):
                for key in keyword_dict.keys():
                    if key in default_keyword_dict:
                        self.keyword_dict[key] = default_keyword_dict[key]
                print("Self keyword dict:\n")
                print(self.keyword_dict)
            elif isinstance(keyword_dict, list):
                print(f"Keyword dict: {keyword_dict}")
                for word in keyword_dict:
                    if word in keyword_dict:
                        self.keyword_dict[word] = default_keyword_dict[word]
                print("Self keyword dict from List:\n")
                print(self.keyword_dict)
        listener = self.listen()
        print("Listener initiated...")
        logger.info(f"Listener initiated...")
        Export(listener, export_interval)

    def listen(self):
        keyword_obj = Keywords(self.keyword_dict)
        listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3],keyword_obj)
        print("Stream running...")
        logger.info("Stream running...")
        listener.filter(track = keyword_obj.keyword_lst, languages=["en","de"], threaded = True)
        return listener
    
#Method to allow the script to be executed via terminal
def parse_args():
    parser = argparse.ArgumentParser(description='Runner for Twitter Listener')
    parser.add_argument("-k", "--keywords", type=str, required=True,
                        help="Keywords to filter Stream,Input like = \"btc,eth\". Currently supported btc, eth, ada, bnb, xrp")
    parser.add_argument("-i","--interval",type=float,required=True,
                        help="Exporting to Json in an Interval (min:0.5)")
    args = parser.parse_args()
    return args
    
#for test purposes the script can be executed from the terminal. 
# run python3 runner.py -k "btc,eth,ada" -i 5
if __name__=="__main__":
    keywords = parse_args().keywords.split(",")
    keywords = [word.strip(" []'") for word in keywords]
    interval = parse_args().interval
    # Format for dict
    # dict = {
    #     "btc":["#btc","$btc"],
    #     "ada":["#ada","$ada"],
    # }
    listener = Runner(keywords,interval)
    
