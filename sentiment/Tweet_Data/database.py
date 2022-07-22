# Imports
from venv import create
from requests import session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import sys
Base = declarative_base()
#Config
sys.path.insert(0,"/Users/marvinottersberg/Documents/GitHub/sentiment/") 
from config import ConfigDB
conf = ConfigDB()
#api = conf.create_api("auth1")

#Init DB Connection
#Format: dialect+driver://username:password@host:port/database -> 'postgresql://scott:tiger@localhost/mydatabase'

#Uncomment for local PostgresDB
#engine = create_engine('postgresql://{}:{}@{}/localtweets'.format(conf.USER, conf.PASS, conf.HOST),convert_unicode=True)
#Uncomment for Heroku
engine = create_engine(conf.DB_URL,convert_unicode=True) #echo=True
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
    
