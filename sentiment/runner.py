#!/usr/bin/env python
import os, logging, argparse
from logging.handlers import RotatingFileHandler
from listener import StreamListener
from keywords import Keywords
from datetime import datetime,date, time 
from IPython.display import display
from Tweet_Data.exporter import Export

#Changed this to "sentiment/Logs" for heroku. normally would just say "Logs"
log_dir = 'sentiment/Logs/'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_name = '{}_stream.log'.format(date.today().strftime('%Y%m%d'))
log_handler = RotatingFileHandler(filename=os.path.join(log_dir, log_name), maxBytes=2000000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                    datefmt='%d-%m-%Y T%H:%M:%S')
logger = logging.getLogger(__name__)

#Config
os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config import Config
newconf = Config()

logger = logging.getLogger(__name__)


class Runner():
    def __init__(self,keywords=None,export_interval=10):
        """The Runner starts the listener & exporter with given keyword dictionary

        Args:
            keywords (list optional): List of Keywords
            export_interval (int, optional): Exporting the Data to Json every Interval. Defaults to 10. In Minutes.
        """
        keyword_obj = Keywords(keywords)
        listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3],keyword_obj)
        listener.filter(track = keyword_obj.keyword_lst, languages=["en","de"], threaded = True)
        print("Listener initiated...")
        logger.info(f"Listener initiated...")
        Export(listener, export_interval)
    
#Method to allow the script to be executed via terminal
def parse_args():
    parser = argparse.ArgumentParser(description='Runner for Twitter Listener')
    parser.add_argument("-k", "--keywords", type=str, required=True,
                        help="Keywords to filter Stream,Input like = \"btc,eth\". Currently supported btc, eth, ada, bnb, xrp")
    parser.add_argument("-i","--interval",type=float,required=True,
                        help="Exporting to Json in an Interval (min:0.5)")
    args = parser.parse_args()
    return args
    
# run python3 runner.py -k "btc,eth,ada" -i 5
# if __name__=="__main__":
#     keywords = parse_args().keywords.split(",")
#     keywords = [word.strip(" []'") for word in keywords]
#     interval = parse_args().interval
#     Runner(keywords,interval)


Runner(['btc', 'ada'],0.5)