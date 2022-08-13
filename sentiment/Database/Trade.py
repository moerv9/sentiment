'''
Trade.py
Trade Class to declare the Format and Type of each Column in the Database.
'''
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from .database import Base

class Trade_Table(Base):
    __tablename__ = "trade_data"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    avgTime = Column(DateTime)
    avg = Column(Float, nullable=False)
    tradeAt = Column(DateTime, nullable=False)
    symbol = Column(String(50), nullable=False)
    side = Column(String(10))
    funds = Column(Float)
    fee = Column(Float)
    tradeId = Column(String(200),nullable=False)
    usdt_balance = Column(Float)
    btc_balance = Column(Float)
    
    def __init__(self, avgTime, avg, tradeAt, symbol, side, funds, fee, tradeId, usdt_balance, btc_balance):
        self.avgTime = avgTime
        self.avg = avg
        self.tradeAt = tradeAt
        self.symbol = symbol 
        self.side = side
        self.funds = funds
        self.fee = fee
        self.tradeId = tradeId
        self.usdt_balance = usdt_balance
        self.btc_balance = btc_balance