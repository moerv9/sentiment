# # Imports
# from requests import session
# from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from contextlib import contextmanager
# import sys

# #Config
# #sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/sentiment") 
# from config import Config, ConfigDB
# newconf = Config()
# api = newconf.create_api("auth1")

# #
# engine = create_engine('postgresql://{}:{}@{}/tweets'.format(ConfigDB.USER, ConfigDB.PASS, ConfigDB.HOST),convert_unicode=True)
# Session = scoped_session(sessionmaker(autocommit=False, bind=engine))
# Base = declarative_base()

# @contextmanager
# def session_scope():
#     session = Session()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise 
#     finally:
#         session.close()
        
# def init_db():
#     Base.metadata.create_all(bind=engine,checkfirst=True)
    
