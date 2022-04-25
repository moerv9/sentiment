import os
from tokenize import String
from dotenv import load_dotenv
load_dotenv()
import tweepy
import logging
logger = logging.getLogger(__name__)

class ConfigAPI():
    def __init__(self):
        self.API_KEY = os.getenv('API_KEY')
        self.API_SECRET = os.getenv('API_SECRET')
        self.BEARER_TOKEN = os.getenv('BEARER_TOKEN')
        self.ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
        self.ACCESS_SECRET = os.getenv('ACCESS_SECRET')
    
    def create_api(self,bearer_token:String):
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

class ConfigDB:
    USER = os.environ.get("DB_USER")
    PASS = os.environ.get("DB_PASS")
    HOST = os.environ.get("DB_HOST")


'''
# Test for getting the Tokens
conf = ConfigAPI()
api=conf.create_api("auth1")
print(conf.getKeys())
print(conf.getBearerToken())
'''
