import os

from datetime import  timedelta

class Config:
    SECRET_KEY = os.environ
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/ppoc'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
