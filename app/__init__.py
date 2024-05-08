from flask import Flask,url_for,request,session,jsonify
from flask_sqlalchemy import SQLAlchemy
import flask
import importlib
import os
from dataclasses import dataclass
from .tools.template_global import add_template
import traceback

@dataclass
class Apps:
    name: str
    url_prefix: str = None
    subdomain: str = None
    url_defaults: str = None

    def params(self):
        return {
            "url_prefix" : self.url_prefix,
            "subdomain": self.subdomain,
        }

@dataclass
class Tools:
    App: object = None
    DB: object = None
    Login: object = None
    Babel: object = None
    BabelGetText: object = None
    Request: object = request
    Session: object = session
    LANGUAGES: object = None

    SocketIo : object = None

from . import settings

def create_app():
    app_tools = Tools()
    templates = settings.TEMPLATE_FOLDER
    statics = settings.STATIC_FOLDER
    app = Flask(
        __name__,
        template_folder=templates,
        static_folder=statics,
    )
    app.config.from_object(settings.CONFIG)

    os.makedirs(os.path.join(settings.CONFIG.BASE_APP,templates),exist_ok=True)
    os.makedirs(os.path.join(settings.CONFIG.BASE_APP,statics),exist_ok=True)

    db = SQLAlchemy(app)
    # db.init_app(app)
    # db.app = app

    login = None
    if settings.IS_LOGIN:
        from flask_login import LoginManager
        login = LoginManager(app)
        login.login_view = settings.LOGIN_VIEW
        app_tools.Login = login

    if settings.IS_BABEL:
        from flask_babel import Babel, gettext
        babel = Babel()
        babel.init_app(app)

        babel.BABEL_DEFAULT_LOCALE = settings.BABEL_DEFAULT_LOCALE
        babel.BABEL_DEFAULT_TIMEZONE = settings.BABEL_DEFAULT_TIMEZONE

        app_tools.Babel = babel
        app_tools.BabelGetText = gettext

        # app.config["BABEL_TRANSLATION_DIRECTORIES"] = "babel"
        app.config["DEFAULT_BABEL_LOCALE"] = "zh"
        LANGUAGES = {
            "zh": "Chinese",
            "en": "English",
            "ja": "Japanese"
        }
        app_tools.LANGUAGES = LANGUAGES

        @babel.localeselector
        def get_locale():
            # print("==========>>>>>>>" ,LANGUAGES)
            # return request.accept_languages.best_match(LANGUAGES.keys())
            return session.get('lang', 'en')

    if hasattr(settings,"IS_SOCKETIO") and settings.IS_SOCKETIO:
        from flask_socketio import SocketIO
        socketio = SocketIO(app)
        app_tools.SocketIo = socketio

    settings.IS_CSRF=True
    if settings.IS_CSRF:
        # from flask_wtf import CSRFProtect
        from flask_wtf.csrf import CSRFProtect,CSRF,CSRFError

        import flask_wtf
        # from flask_wtf.csrf import CsrfProtect
        csrf = CSRFProtect(app)

        # @app.errorhandler(400)
        # def csrf_error(reason) :
        #     print("=========>>>>>>>>>>>",reason)
        #     return jsonify({"k":1})

    # from .user import main
    # app.register_blueprint(main)

    app_tools.App = app
    app_tools.DB = db

    return app,db,login,app_tools
app,db,login,app_tools = create_app()

class PubConfigMethod(object):
    def __init__(self):
        self.config_obj = settings.CONFIG
        self.blue_app = {}
        self.blue_url_map = {}

    def insert_blue_app(self,app):
        app_list = settings.INSTALLED_APPS
        for blue_app in app_list:
            # try:
            #     importlib.import_module(f"{self.config_obj.BASE_APP}.{blue_app}.views")
            # except Exception as e:
            #     pass
            cur_blue_app = self.get_blue_app(blue_app.name)
            app.register_blueprint(cur_blue_app,**blue_app.params()) #,url_prefix="/user")
            # app.register_blueprint(cur_blue_app,**{'url_prefix': None}) #,url_prefix="/user")

            try:
                importlib.import_module(f"{self.config_obj.BASE_APP}.{blue_app.name}.models")
            except Exception as e:
                print("model E: ",e,f"{self.config_obj.BASE_APP}.{blue_app.name}.models")
                pass

    def get_blue_app(self,blue_app):
        if "." in blue_app:
            blue_app_key = '.'.join(blue_app.split(".")[:2])
        else:
            blue_app_view = f"{self.config_obj.BASE_APP}.{blue_app}.views"
            blue_app_key = '.'.join(blue_app_view.split(".")[:2])

        if blue_app_key not in self.blue_app:
            print("Blueprint: ",blue_app_key)
            blue_app_obj = flask.Blueprint(blue_app_key,blue_app_key)
            self.blue_app[blue_app_key] = blue_app_obj

            try:
                # importlib.import_module("app.user.views")
                importlib.import_module(blue_app_view)
            except Exception as e:
                print("E: ",e,blue_app_view)
                traceback.print_exc()
        else:
            blue_app_obj = self.blue_app[blue_app_key]
        return blue_app_obj

    def model_tablename(self,obj, name):
        tn = "__tablename__"
        table_name = getattr(obj, tn) if hasattr(obj, tn) else obj
        return f"{table_name}.{name}"

    def blue_url_for(self,et,**kwargs):
        blue_url_map = self.blue_url_map
        for ett in [et,*[f"{i}.{et}" for i in pm.blue_app.keys()]]:
            if ett in blue_url_map:
                return url_for(ett,**kwargs)
            try:
                url = url_for(ett,**kwargs)
                blue_url_map[ett] = ""
                return url
            except Exception as e:
                pass
        return ""

pm = PubConfigMethod()
pm.insert_blue_app(app)

add_template(app,pm,app_tools)
from .tools import error_handler

