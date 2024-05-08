from flask import render_template,redirect,url_for,request,flash,jsonify,make_response,session
from flask_login import login_user, logout_user, current_user, login_required

from ..tools.params_req import BaseResponseParams
from .. import pm

from functools import wraps

def sign_user_role(*sargs,**skwargs):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if not current_user.is_authenticated:
                return redirect(pm.blue_url_for("user_login"))
            if sargs and current_user.role not in sargs :
                return redirect(pm.blue_url_for("user_login"))

            return f(*args, **kwargs)
        return decorated_function

    return decorator
