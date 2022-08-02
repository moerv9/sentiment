#!/usr/bin/env python
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
#This whole keyword class could be improved and the check_keyword function from inside on_status should be in here but it works for now
class Keywords():
    def __init__(self,keyword_dict):
        self.keyword_dict = {}
        try:
            if keyword_dict is None: 
                self.keyword_dict = default_keyword_dict
            else:
                if isinstance(keyword_dict, dict):
                    for key in keyword_dict.keys():
                        if key in default_keyword_dict:
                            self.keyword_dict[key] = default_keyword_dict[key]
                elif isinstance(keyword_dict, list):
                    for word in keyword_dict:
                        if word in keyword_dict:
                            self.keyword_dict[word] = default_keyword_dict[word]
        except:
            logger.warning("Error in Keyword input")

        self.keyword_lst = self.build_keyword_list()
        #print(self.keyword_lst)
        #logger.info(self.keyword_lst)
        
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
            String: returns keyword or None, crypto_identifier from dict
        """
        # i =0 
        # for val in list(self.keyword_dict.items()):
            # This looks for keyword like "btc" or "ada" -> results in lots of unrelated tweets 
            # if re.search(rf"\b{key}\b", body, re.IGNORECASE):  
            #     return key, list(self.keyword_dict.keys())[i]
            # for keyword in val:
            #     if keyword.lower() in body:
            #         return keyword, list(self.keyword_dict.keys())[i]
            # i+=1
        # if any([key in body for key in self.keyword_lst]):
        #     print(body)
        for val in self.keyword_lst:
            if val in body:
                return val
        else:
            return None
                