import os, logging, datetime, argparse
from logging.handlers import RotatingFileHandler
from listener import StreamListener
from IPython.display import display
import pandas as pd

#Config
#os.sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/")
from config_sent import ConfigAPI
newconf = ConfigAPI()


log_dir = 'Logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_name = '{}_stream.log'.format(datetime.date.today().strftime('%Y%m%d'))
log_handler = RotatingFileHandler(filename=os.path.join(log_dir, log_name), maxBytes=2000000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                    datefmt='%d-%m-%Y T%H:%M:%S')


keywords = {
    "btc": ["btc","#btc","$btc","bitcoin"],
    "ada": ["ada","#ada","$ada","cardano"],
    "eth": ["eth","#eth","$eth","ether","ethereum","etherum"],
    "bnb": ["bnb","#bnb","$bnb","binance coin"],
    "xrp": ["xrp","#xrp","$xrp","ripple"],
}

if __name__ == '__main__':
    keywords = keywords["btc"]
    listener = StreamListener(newconf.getKeys()[0],newconf.getKeys()[1],newconf.getKeys()[2],newconf.getKeys()[3],keywords)
    logging.info(f"Starting stream: {keywords}")
    print("Stream running...")
    listener.filter(track = keywords, languages=["en","de"], threaded = True)
    #print(f"Avg Sentiment: {listener.sent_avg}")