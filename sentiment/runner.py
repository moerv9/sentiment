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
from config_sent import ConfigAPI
newconf = ConfigAPI()


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
        logger.info("1")
        self.keyword_dict = {}
        if keyword_dict is None: 
            self.keyword_dict = default_keyword_dict
        else:
            for key in keyword_dict.keys():
                if key in default_keyword_dict:
                    self.keyword_dict[key] = default_keyword_dict[key]
            print("Self keyword dict:\n")
            print(self.keyword_dict)
        listener = self.listen()
        print("Listener initiated...")
        logger.info(f"Listener initiated...")
        Export(listener, export_interval)

    def listen(self):
        logger.info("3")
        keyword_obj = Keywords(self.keyword_dict)
        listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3],keyword_obj)
        print("Stream running...")
        logger.info("Stream running...")
        listener.filter(track = keyword_obj.keyword_lst, languages=["en","de"], threaded = True)
        return listener
    
        

if __name__=="__main__":
    testdict = {
        "btc":["#btc","$btc"],
        "ada":["#ada","$ada"],
    }
    listener = Runner(testdict,0.5)
    