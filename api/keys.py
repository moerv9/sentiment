import os
from dotenv import load_dotenv
load_dotenv()

def getKeys():
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    BEARER_TOKEN = os.getenv('BEARER_TOKEN')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ACCESS_SECRET = os.getenv('ACCESS_SECRET')
    return API_KEY, API_SECRET, BEARER_TOKEN,ACCESS_TOKEN,ACCESS_SECRET

