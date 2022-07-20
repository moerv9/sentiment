# Imports
from venv import create
from requests import session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import sys
Base = declarative_base()
#Config
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/") 
from config import Config, ConfigDB
conf = ConfigDB()
#api = conf.create_api("auth1")

#Init DB Connection
#Format: dialect+driver://username:password@host:port/database
#engine = create_engine('postgresql://{}:{}@{}/tweets'.format(ConfigDB.USER, ConfigDB.PASS, ConfigDB.HOST),convert_unicode=True) #'postgresql://scott:tiger@localhost/mydatabase'
#engine=create_engine(f"postgresql://{conf.USER_HEROKU}:{conf.PASS_HEROKU}@{conf.HOST_HEROKU}:5432/d2vfhe1prooh9b",convert_unicode=True)
engine = create_engine(conf.DATABASE_URL,echo=True,convert_unicode=True)
Session = scoped_session(sessionmaker(autocommit=False, bind=engine))


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise 
    finally:
        session.close()
        
def init_db():
    Base.metadata.create_all(bind=engine,checkfirst=True)
    
