from flask import session
from flask_login import UserMixin  # 引入用户基类
from werkzeug.security import generate_password_hash,check_password_hash
from .. import db,login,app_tools,pm
import datetime,json, random,decimal

_ = app_tools.BabelGetText

COMMON = "common"
SuperAdmin = "super_admin"

ROLE_CHOICES = (
        (COMMON, _("用户")),
        (SuperAdmin, _("超级管理员")),
    )

KIND_ARTICLE_CHOICES = (
    ("一级", _("一级")),
    ("二级", _("二级")),
    ("三级", _("三级")),
    ("四级", _("四级")),
    ("五级", _("五级")),
)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin,db.Model):
    # __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    role = db.Column(db.String(128),default=COMMON)

    info = db.relationship("UserDetails", uselist=False, backref="own")


    def __init__(self, username):
        self.username = username

    @property
    def get_role_display(self):
        try:
            rc = dict(list(ROLE_CHOICES))
        except Exception as e :
            print("E: ", e)
        return rc.get(self.role,COMMON)
    def is_role(self,name):
        rc = dict(list(ROLE_CHOICES))
        return name in rc

    @property
    def get_user_name(self):
        name = ""
        if self.info :
            name = self.info.name
        else :
            name = self.username
        return name

    @property
    def is_role_common(self):
        if self.role in [SuperAdmin]:
            return False
        return True

    @property
    def is_role_superadmin(self):
        if self.role == SuperAdmin :
            return True
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        return None

    @property
    def get_pic(self):
        if not self.info or not self.info.pic:
            return "/statics/assets/avatars/profile-pic.jpg"
        else :
            return f"/statics/user_img_thumb/{self.info.pic}"

    @property
    def get_price(self):
        if not self.info :
            return 0
        return self.info.price

class UserDetails(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    stu_id = db.Column(db.Integer, db.ForeignKey(User.id), comment="外键")

    pic = db.Column(db.String(255),default="")

    name = db.Column(db.String(255),default="")
    phone = db.Column(db.String(255),default="")
    address = db.Column(db.String(255),default="")

    age = db.Column(db.Integer,default=0)
    sex_choice = [
        ("no",_("未填写")),
        ("male",_("男性")),
        ("female", _("女性")),
    ]
    sex = db.Column(db.String(12),default="no")
