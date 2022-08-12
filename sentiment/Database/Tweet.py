'''
Tweet.py
Tweet Class to declare the Format and Type of each Column in the Database.
'''
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from .database import Base

class Tweet(Base):
    __tablename__ = "tweet_data"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    body = Column(String(5000), nullable=False)
    keyword = Column(String(256), nullable=False)
    tweet_date = Column(DateTime, nullable=False)
    location = Column(String(100))
    verified_user = Column(Boolean)
    followers = Column(Integer)
    user_since = Column(DateTime,nullable=False)
    sentiment = Column(Float)
    
    def __init__(self, body, keyword, tweet_date, location, verified_user, followers, user_since, sentiment):
        self.body = body
        self.keyword = keyword
        self.tweet_date = tweet_date
        self.location = location
        self.verified_user = verified_user
        self.followers = followers
        self.user_since = user_since
        self.sentiment = sentiment
        
    def __repr__(self):
        return "<Tweet %r>" %self.body
    

    