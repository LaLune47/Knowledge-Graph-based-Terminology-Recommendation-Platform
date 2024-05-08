from . import *
import importlib
import flask
basedir=os.path.abspath(os.path.dirname(__file__))

SQL_MYSQL,SQL_SQLITE = "mysql","sqlite"

class PubConfigMethod(object):
    def __init__(self):
        self.config = {}
        self.blue_app = {}
        self.config_obj = None

    def register_config(self,obj,name=""):
        name = name if name else obj.__name__
        self.config[name] = obj

    def import_config(self):
        base_name = os.path.basename(basedir)
        cur_file = os.path.basename(__file__).rsplit(".",1)[0]
        for f in os.listdir(basedir):
            file_name = os.path.basename(f)
            file_name = file_name.rsplit(".",1)[0]
            if cur_file == file_name:
                continue
            if not file_name.startswith("config"):
                continue
            importlib.import_module(f"{base_name}.{file_name}")

    def get_config(self,name):
        try:
            return self.config[name]
        except Exception as e:
            print("config error choose: ",list(self.config.keys()))
            return self.config[list(self.config.keys())[0]]

    @staticmethod
    def sql_url(DATABASE, USERNAME="", PASSWORD="", PORT="", HOSTNAME="", sql=SQL_SQLITE):
        if sql == SQL_MYSQL:
            HOSTNAME = '127.0.0.1' if not HOSTNAME else HOSTNAME
            PORT = '3306' if not PORT else PORT
            DATABASE = DATABASE
            USERNAME = 'root' if not USERNAME else USERNAME
            PASSWORD = 'root' if not PASSWORD else PASSWORD
            DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
            SQLALCHEMY_DATABASE_URI = DB_URI
        elif sql == SQL_SQLITE:
            SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(basedir), f'{DATABASE}.db')
        return SQLALCHEMY_DATABASE_URI

    def set_basedir(self,dir,config):
        config.BASE_APP_DIR = dir
        config.BASE_DIR  = os.path.dirname(dir)
        config.BASE_APP = os.path.basename(dir)


pm = PubConfigMethod()