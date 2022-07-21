
#This whole keyword class could be improved and the check_keyword function from inside on_status should be in here but it works for now
class Keywords():
    def __init__(self,keyword_dict):
        self.keyword_dict = keyword_dict
        self.keyword_lst = self.build_keyword_list()
        
    def build_keyword_list(self):
        """Build a list of keywords from a dictionary. Appends the values after the key
        Needed for the Tweet Listener.Filter
        Returns:
            list: comma separated list of keywords. 
        """
        new_list = []
        for key, val in self.keyword_dict.items():
            new_list.append(key)
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
        i =0 
        for val in list(self.keyword_dict.items()):
            # This looks for keyword like "btc" or "ada" -> results in lots of unrelated tweets 
            # if re.search(rf"\b{key}\b", body, re.IGNORECASE):  
            #     return key, list(self.keyword_dict.keys())[i]
            for keyword in val:
                if keyword.lower() in body:
                    return keyword, list(self.keyword_dict.keys())[i]
            #print(f"KEY: {list(self.keyword_dict.keys())[i]}")
            i+=1
        
        return None, None
        