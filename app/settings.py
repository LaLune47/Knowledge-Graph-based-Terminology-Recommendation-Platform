import os
from config import pm
from . import Apps

BASE_APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = pm.get_config("default")
pm.set_basedir(BASE_APP_DIR,CONFIG)

CONFIG.DEBUG = True

INSTALLED_APPS = [
    Apps(name="user",url_prefix="/"),
    Apps(name="user",url_prefix="/user"),
    # Apps(name="article", url_prefix="/article"),
]

TEMPLATE_FOLDER = "templates"
STATIC_FOLDER = "statics"

IS_LOGIN = True
LOGIN_VIEW = "app.user.user_login"
LOGIN_INDEX = "user_details"

IS_BABEL = True
BABEL_DEFAULT_LOCALE = "zh"
BABEL_DEFAULT_TIMEZONE = "UTC"
BABEL_TRANSLATION_DIRECTORIES = "babel/translations"

IS_SOCKETIO = True


GRAPH_URL = "http://localhost:7474"
GRAPH_USERNAME = "neo4j"
GRAPH_PASSWORD = "changgong"