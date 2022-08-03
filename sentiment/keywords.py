'''
keywords.py
Initially designed to work for multiple coins, thus the Keyword dict. 
Just set the keywords in the runner.py to "btc,ada,eth,bnb,xrp" to search for all these coins.
For simplification and to not overload the Database I've just searched for Bitcoin.

'''
import os, logging, argparse
from logging.handlers import RotatingFileHandler
import re

logger = logging.getLogger(__name__)
default_keyword_dict ={
                "btc":["$btc","#btc","bitcoin","#bitcoin"],
                "ada":["#ada","$ada","cardano"],
                "eth":["#eth","$eth","ether","ethereum","etherum"],
                "bnb":["#bnb","$bnb","binance coin"],
                "xrp":["#xrp","$xrp","ripple"],
}
class Keywords():
    def __init__(self,keywords):
        """Keyword Class if you want to search for multiple coins.

        Args:
            keywords (list): Keywords seperated like "btc,ada,eth"
        """
        self.keyword_dict = {}
        try:
            if keywords is None: 
                self.keyword_dict = default_keyword_dict
            else:
                if isinstance(keywords, dict):
                    for key in keywords.keys():
                        if key in default_keyword_dict:
                            self.keyword_dict[key] = default_keyword_dict[key]
                elif isinstance(keywords, list):
                    for word in keywords:
                        if word in keywords:
                            self.keyword_dict[word] = default_keyword_dict[word]
        except:
            logger.warning("Error in Keyword input")

        self.keyword_lst = self.build_keyword_list()

    def build_keyword_list(self):
        """Build a list of keywords from a dictionary. Appends the values from the default_keyword_dict to a new list.
        Needed for the Tweet Listener.Filter
        Returns:
            list: comma separated list of keywords like: 
            ['#btc', '$btc', 'bitcoin', '#bitcoin', '#ada', '$ada', 'cardano']
        """
        new_list = []
        for key, val in self.keyword_dict.items():
            for i in val:
                new_list.append(i)
        return new_list
        
    def check_keyword(self,body):
        """Check Tweet for keywords
        Args:
            body (String): Tweet Text
        Returns:
            String: returns keyword or None
        """
        for val in self.keyword_lst:
            if val in body:
                return val
        else:
            return None