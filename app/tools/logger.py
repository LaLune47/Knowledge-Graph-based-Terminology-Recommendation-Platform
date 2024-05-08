from flask_login import current_user
from .. import app,pm,db,app_tools

_ = app_tools.BabelGetText

import logging
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("log.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)s %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(lineno)s %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

class Logger:

    def debug(self,message):
        message = _(message)
        if current_user.is_authenticated :
            logger.debug(f"{current_user.username}({current_user.role}): {message}")
        else :
            logger.debug(f"{message}")

logger_method = Logger()