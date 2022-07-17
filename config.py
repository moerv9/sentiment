import os
from dotenv import load_dotenv
load_dotenv()
import tweepy
import logging
logger = logging.getLogger(__name__)
from boto.s3.connection import S3Connection

s3_handler = S3Connection(os.environ['API_KEY'], os.environ['API_SECRET'],os.environ['ACCESS_TOKEN'],os.environ['ACCESS_SECRET'],os.environ['HEROKU_DATABASE_URL'])

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
        self.USER = os.environ.get("DB_USER")
        self.PASS = os.environ.get("DB_PASS")
        self.HOST = os.environ.get("DB_HOST")
        self.HEROKU_DATABASE_URL = os.environ["HEROKU_DATABASE_URL"]
    
    def getKeys(self):
        #logger.info("got Keys")
        return self.USER, self.PASS,self.HOST, self.HEROKU_DATABASE_URL

# Config for Binance API
class ConfigBinance:
    def __init__(self) -> None:
        self.BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
        self.BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
        self.BINANCE_TESTNET_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
        self.BINANCE_TESTNET_API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")
        
    def getKeys(self,testnet:bool=False):
        if testnet:
            logger.info("Retrieve Binance Testnet Keys")
            return self.BINANCE_TESTNET_API_KEY,self.BINANCE_TESTNET_API_SECRET
        else:
            logger.info("Retrieve Binance API Keys")
            return self.BINANCE_API_KEY,self.BINANCE_API_SECRET

'''
# Test for getting the Tokens
conf = ConfigAPI()
api=conf.create_api("auth1")
print(conf.getKeys())
print(conf.getBearerToken())
'''