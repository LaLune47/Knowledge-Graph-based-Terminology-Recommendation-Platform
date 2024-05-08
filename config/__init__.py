import os
from datetime import timedelta
from .tools import pm

class Config:
    FLASK_ENV = "production" # production development

    SSL_DISABLE = True
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    SQLALCHEMY_RECORD_QUERIES=True
    FLASK_SLOW_DB_QUERY_TIME=0.5

    SECRET_KEY = 'group-10-is-the-best'
    SQLALCHEMY_DATABASE_URI = pm.sql_url("db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY='huu cool'
    SESSION_COOKIE_NAME = "programmer_session"
    PERMANENT_SESSION_LIFETIME: timedelta(days=31)

    TEMPLATE_FOLDER = "templates"
    STATIC_FOLDER = "statics"

    BASE_DIR = ""
    BASE_APP_DIR = ""
    BASE_APP = ""
    BABEL_TRANSLATION_DIRECTORIES = "../babel/translations"

pm.register_config(Config,"default")

pm.import_config()
pm.config_obj = Config
