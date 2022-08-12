import os
from dotenv import load_dotenv
load_dotenv()
import tweepy
import logging
logger = logging.getLogger(__name__)
from boto.s3.connection import S3Connection



# Get Twitter API Token and Secret
class Config():
    def __init__(self):
            self.API_KEY = os.getenv('API_KEY')
            self.API_SECRET = os.getenv('API_SECRET')
            self.BEARER_TOKEN = os.getenv('BEARER_TOKEN')
            self.ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
            self.ACCESS_SECRET = os.getenv('ACCESS_SECRET')
            self.create_api("auth1")
        
    def create_api(self,bearer_token):
        """Returns api

        Args:
            bearer_token: can be "bearer" or "auth1" to choose with what token the API will be initialised

        Returns:
            The API

        Raises:
            VerificationError: Error creating the API
        """
        if bearer_token == "bearer":
            auth = tweepy.OAuth2BearerHandler(self.BEARER_TOKEN)
        elif bearer_token == "auth1":
            auth = tweepy.OAuth1UserHandler(self.API_KEY, self.API_SECRET, self.ACCESS_TOKEN, self.ACCESS_SECRET)
            
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        try:
            api.verify_credentials()
        except Exception as e:
            logger.error("Error creating API", exc_info=True)
            raise e
        #logger.info("API created")
        return api
    
    def getKeys(self):
        #logger.info("got Keys")
        return self.API_KEY, self.API_SECRET,self.ACCESS_TOKEN, self.ACCESS_SECRET
    
    def getBearerToken(self):
        #logger.info("got Bearertoken")
        return self.BEARER_TOKEN

#Keys for Posgres Database
class ConfigDB:
    def __init__(self):
            # Uncomment for local Postgres DB
            # self.USER = os.environ["DB_USER"]
            # self.PASS = os.environ["DB_PASS"]
            # self.HOST = os.environ["DB_HOST"]
            # self.DBNAME_HEROKU = os.environ["DBNAME_HEROKU"]
            # self.HOST_HEROKU = os.environ["HOST_HEROKU"]
            # self.USER_HEROKU = os.environ["USER_HEROKU"]
            # self.PASS_HEROKU = os.environ["PASS_HEROKU"]
            
        USER = os.environ.get("DB_USER")
        PASS = os.environ.get("DB_PASS")
        HOST = os.environ.get("DB_HOST")
        self.DB_URL = os.environ.get("DB_URL")

# Config for Binance API
class ConfigBinance:
    def __init__(self) -> None:
        self.BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
        self.BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
        self.BINANCE_TESTNET_API_KEY = os.environ.get("BINANCE_TESTNET_API_KEY")
        self.BINANCE_TESTNET_API_SECRET = os.environ.get("BINANCE_TESTNET_API_SECRET")
        
    def getKeys(self,testnet:bool=False):
        if testnet:
            #logger.info("Retrieve Binance Testnet Keys")
            return self.BINANCE_TESTNET_API_KEY,self.BINANCE_TESTNET_API_SECRET
        else:
            #logger.info("Retrieve Binance API Keys")
            return self.BINANCE_API_KEY,self.BINANCE_API_SECRET

class ConfigKucoin:
    def __init__(self) -> None:
        self.KUCOIN_UID = os.environ.get("KUCOIN_UID")
        self.KUCOIN_KEY = os.environ.get("KUCOIN_API_KEY")
        self.KUCOIN_SECRET = os.environ.get("KUCOIN_SECRET")
        self.KUCOIN_PASS = os.environ.get("KUCOIN_PASS")
        self.KUCOIN_SUB_KEY = os.environ.get("KUCOIN_SUB_KEY")
        self.KUCOIN_SUB_SECRET = os.environ.get("KUCOIN_SUB_SECRET")
        self.KUCOIN_SUB_PASS = os.environ.get("KUCOIN_SUB_PASS")

'''
# Test for getting the Tokens
conf = ConfigAPI()
api=conf.create_api("auth1")
print(conf.getKeys())
print(conf.getBearerToken())
'''