from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(Config)
# Variable global para controlar el tema
app.config['THEME'] = 'light'  # Tema inicial claro

db = SQLAlchemy(app)

from app import routesadmin
from app import routesparti
