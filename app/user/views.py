from flask import render_template,redirect, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from .. import pm,db,app_tools
import os,time
_ = app_tools.BabelGetText
from . import models
from .. import settings
from ..tools.pager import PageInfo
from ..tools.params_req import BaseResponseParams
from ..tools.json_params import JsonBaseResponse
from ..tools.role_sign import sign_user_role
from ..tools.logger import logger_method
from app.tools.neo4j_handler import graph_handler

from py2neo import Node, Relationship, RelationshipMatcher

from .item_array import terms_array
from .item_array import terms_array_details
import random

view = pm.get_blue_app(__name__)

@view.route("/set_language")
def set_language() :
    lanaguae = session.get('lang', 'en') #request.accept_languages.best_match(app_tools.LANGUAGES.keys())
    change_language = "en" if lanaguae == "zh" else "zh"
    print("language: ",lanaguae,change_language)

    # response.headers.add("Accept-Language", change_language)
    # response.headers["Accept-Language"] = change_language
    session['lang'] = change_language

    req_params = BaseResponseParams(request)
    print(req_params.next_url)
    return redirect(req_params.next_url)

@view.route('/login', methods=['GET', 'POST'],endpoint="user_login")
def login():
    req_params = BaseResponseParams(request)

    if req_params.POST:
        json_params = JsonBaseResponse()

        if current_user.is_authenticated:
            logout_user()
        if req_params.username and req_params.password:
            pass
        else:
            return json_params.toJson(code=303,message="Invalid username or password")

        user = models.User.query.filter_by(username=req_params.username).first()
        # if user is None or not user.check_password(""):
        #     return redirect(url_for('login'))
        if user and user.verify_password(req_params.password):
            login_user(user)
        else:
            return json_params.toJson(code=503, message="Invalid password")

        next_page = request.args.get('next',"")
        print("next_page: ", next_page)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = pm.blue_url_for(settings.LOGIN_INDEX) if settings.LOGIN_INDEX else "/"
        print("next_page: ", next_page)
        logger_method.debug(f"用户登录成功")
        return json_params.toJson(data={"next_page":next_page})
    return render_template('user/login.html',req_params=req_params)

@view.route('/register', methods=['GET', 'POST'],endpoint="user_register")
def register():
    req_params = BaseResponseParams(request)
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    if req_params.POST:
        json_params = JsonBaseResponse()
        if False : #or not req_params.code :
            return json_params.toJson(code=306, message=_("验证码不能为空！"))
        if req_params.username \
                and req_params.password \
                and req_params.password == req_params.repassword:
                # and req_params.code:

            # if req_params.code != models.SendEmail.get_email_code(req_params.username) :
            #     return json_params.toJson(code=305,message=_("验证码错误！"))

            try:
                user = models.User(username=req_params.username)
                user.set_password(req_params.password)
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                json_params.set_msg(301,_("用户已存在"))
        else:
            json_params.set_msg(302, _("参数传入不全！"))
        logger_method.debug(f"用户注册成功")
        return json_params.toJson()
    return render_template('user/login.html',req_params=req_params,status="register")
    # return render_template('base.html',req_params=req_params,status="register")

@view.route('/logout',endpoint="user_logout")
@login_required
def logout():
    logout_user()
    return redirect(pm.blue_url_for("user_login"))

@view.route("/show_all_users")
@sign_user_role(models.SuperAdmin)
# @login_required
def show_all_users() :
    req_params = BaseResponseParams(request)

    search = req_params.search
    if search :
        users = models.User.query.filter(
            models.User.username.like("%" + search + "%")
        )
    else :
        users = models.User.query.filter()

    page_info = PageInfo(request.args.get('page', None), users.count(), perItems=10,
                         path=f'{request.path}?search={search}&',
                         ormObjs=users, open_id=False,
                         )
    admins = page_info.page_objs

    return render_template("user/show_all_users.html",admins=admins,page_info=page_info,req_params=req_params, user_role_details=models.ROLE_CHOICES)

@view.route("/change_user",methods=["POST"])
def change_user() :
    req_params = BaseResponseParams(request)
    json_params = JsonBaseResponse()

    print("params: ", req_params)

    if request.method == "GET" :
        return json_params.toJson(code="207",message=_("数据请求失败！"))

    nid = req_params.nid
    try:
        obj = models.User.query.get(nid)
    except Exception as e :
        return json_params.toJson(code=201,message=_("用户不存在！"))

    try:
        assert req_params.data
    except Exception as e :
        return json_params.toJson(code=205,message=_("输入信息不能为空！"))

    try:
        data = {}
        if req_params.symbol == "username" :
            obj.username = req_params.data
        if req_params.symbol == "password" :
            obj.set_password(req_params.data)
        if req_params.symbol == "role" :
            print("req_params.data: ", req_params.data)
            if not obj.is_role(req_params.data) :
                return json_params.toJson(code=202,message=_("角色不存在"))
            obj.role = req_params.data
            data["role"] = obj.get_role_display
        db.session.commit()
        return json_params.toJson(code=200,data=data)
    except Exception as e :
        return json_params.toJson(code=203,message=_("异常报错"))

@view.route("/user_details",methods=["GET","POST"])
@sign_user_role(models.SuperAdmin, models.COMMON)
def user_details() :
    req_params = BaseResponseParams(request)
    sex_choices = models.UserDetails.sex_choice
    print("sex_: ",sex_choices)

    if req_params.POST :
        json_params = JsonBaseResponse()
        user_number = req_params.user_number
        user_name = req_params.user_name
        user_phone = req_params.user_phone
        user_sex = req_params.user_sex
        user_age = req_params.user_age
        user_address = req_params.user_address

        user_details = {
            "name" : user_name,
            "age": user_age,
            "address": user_address,
            "sex": user_sex,
            "phone" : user_phone,
        }

        try :
            assert current_user.info
            models.UserDetails.query.filter(models.UserDetails.stu_id == current_user.id).update(
                user_details
            )
        except Exception as e :
            current_user.info = models.UserDetails(
                ** user_details
            )
        db.session.commit()

        return json_params.toJson(code=200, data=user_details)

    return render_template(
            "user/user_details.html",
            req_params = req_params ,
            sex_choices = sex_choices,
            address_count = 0,
            pay_settings = None,
           )

@view.route("/user_thumb_upload",methods=["POST"])
def user_thumb_upload() :
    print("user_thumb_upload: ", user_thumb_upload)
    file = request.files.get("file")
    if not file :
        return jsonify({"code":101})
    print("file: ", file)
    save_path = "./app/statics/user_img_thumb"
    os.makedirs(save_path, exist_ok=True)

    pic = str((time.time() * 1000)) + ".jpg"

    file.save(os.path.join(save_path, pic))

    pic_path = f"/statics/user_img_thumb/{pic}"

    try :
        assert current_user.info
        models.UserDetails.query.filter(models.UserDetails.stu_id == current_user.id).update(
            {
                "pic" : pic,
            }
        )
    except Exception as e :
        current_user.info = models.UserDetails(pic = pic)
    db.session.commit()

    return jsonify({"code":200,"pic":pic_path})

@view.route("/change_user_details",methods=["GET","POST"])
def change_user_details() :
    req_params = BaseResponseParams(request)
    sex_choice = models.UserDetails.sex_choice

    if request.method == "POST" :
        userDetails = {
            "name" : req_params.name,
            "phone": req_params.phone,
            "address": req_params.address,
            "age": req_params.age,
            "sex": req_params.sex,
        }
        try:
            assert current_user.info
            models.UserDetails.query.filter(models.UserDetails.stu_id==current_user.id).update(userDetails)
        except Exception as e :
            current_user.info = models.UserDetails(**userDetails)
            # db.session.add(user_detail)
        # current_user.info.name = req_params.name
        db.session.commit()
    else :
        req_params.get_obj_params(current_user.info)

    return render_template("user/change_user_details.html",
                           req_params = req_params,
                           sex_choice = sex_choice,
                           )

@view.route("/change_user_password",methods=["GET","POST"])
def change_user_password() :
    req_params = BaseResponseParams(request)
    json_params = JsonBaseResponse()

    user_email = req_params.user_email
    user_password = req_params.user_password
    user_code = req_params.user_code

    try:
        obj = models.User.query.filter_by(username=user_email).first()
        assert obj
    except Exception as e :
        return json_params.toJson(code=201,message=_("用户不存在！"))

    code = models.SendEmail.get_email_code(user_email)
    if code != user_code :
        return json_params.toJson(code=202, message=_("用户验证码错误！"))

    obj.set_password(user_password)
    db.session.commit()
    return json_params.toJson(code=200, data={})

@view.route("/delete_article_nid/<nid>", methods=["GET","POST"])
def delete_article_nid(nid):
    req_params = BaseResponseParams(request)
    json_params = JsonBaseResponse()

    try:
        models.ArticleDetails.query.filter(models.ArticleDetails.id == nid).delete()
        db.session.commit()
    except Exception as e :
        return redirect(pm.blue_url_for("show_all_articles"))

    return redirect(pm.blue_url_for("show_all_articles"))

@view.route("/")
@view.route("/show_all_articles")
def show_all_articles():
    req_params = BaseResponseParams(request)

    search = req_params.search
    if search:
        sql = f"MATCH (n:{search}) WHERE NOT '用户' IN labels(n)  RETURN n"
    else:
        sql = "MATCH (n) WHERE NOT '用户' IN labels(n) RETURN n"

    articles = graph_handler.graph.run(sql).data()

    page_info = PageInfo(request.args.get('page', None), len(articles), perItems=15,
                         path=f'{request.path}?search={search}&',
                         ormObjs=articles, open_id=False,
                         )

    articles = []
    for i in page_info.page_objs:
        articles.append({
            "name": i["n"]["name"],
            "en": i["n"]["en"],
            "label": str(i["n"].labels).strip(":")
        })



    return render_template(
        "user/show_article_details.html",
        articles=articles,
        page_info=page_info,
        req_params=req_params,
        kind_choices=models.KIND_ARTICLE_CHOICES,
    )

@view.route("/show_article_details/<nid>")
@login_required
def show_article_details(nid) :
    req_params = BaseResponseParams(request)

    sql = f"MATCH (n) WHERE n.name = '{nid}' RETURN n"
    res = graph_handler.graph.run(sql).data()
    search_obj = res[0]["n"]

    graph = graph_handler.graph

    node2_label = "用户"
    graph.merge(
        Node("用户", name=current_user.id),
        "用户",
        "name"
    )


    obj = {
        "name":search_obj["name"],
        "en": search_obj["en"],
        "label": str(search_obj.labels).strip(":")
    }

    # 获取或创建节点
    node1 = graph.nodes.match(obj["label"], **{"name": obj["name"]}).first()

    node2_key = "name"
    node2 = graph.nodes.match(node2_label, **{node2_key: current_user.id}).first()

    if node1 and node2:
        # 检查node2和node1之间是否已经存在一个"WATCH"关系
        rel_matcher = RelationshipMatcher(graph)
        rel = rel_matcher.match(nodes=[node2, node1], r_type="WATCH").first()

        if rel:
            # 如果关系存在，增加属性
            rel['count'] = rel.get('count', 0) + 1  # 如果'rel'没有'count'属性，则默认为0并增加1
            graph.push(rel)  # 更新关系
        else:
            # 如果关系不存在，创建它并设置'count'为1
            rel = Relationship(node2, "WATCH", node1, count=1)
            graph.create(rel)

    return render_template("user/show_article_content.html",obj=obj,req_params=req_params)


# 推荐页面
@view.route("/push_to_article")
@login_required
def push_to_article():
    req_params = BaseResponseParams(request)

    sql = f"MATCH p=(n1:用户)-[r]-(n2) where n1.name={current_user.id} RETURN r, n2"
    res = graph_handler.graph.run(sql).data()

    print("========================>>>>>>>>>>>>>>>>>>>>")

    # 点击数据
    click_data = [(item["n2"]["name"], item["r"]["count"]) for item in res]
    # print(click_data)

    # 创建一个字典，将点击数据与术语名称关联
    click_dict = dict(click_data)

    # 创建一个新的列表，包括术语、索引和点击次数
    # 创建一个新的列表，仅包括点击次数大于0的术语、索引和点击次数
    merged_data = [(index, item, click_dict.get(item, 0)) for index, item in enumerate(terms_array) if
                   click_dict.get(item, 0) > 0]
    print(merged_data)

    # todo 替换算法


    results = [index for index, _, _ in merged_data]
    random_number = random.randint(0, 600)
    results.append(random_number)
    random_number = random.randint(0, 600)
    results.append(random_number)
    print(results)

    articles = []
    for index in results:
        if index < len(terms_array_details):
            item = terms_array_details[index]
            articles.append({
                "title": item[0],
                "content": item[1],
                "get_kind_display": item[2]
            })

    return render_template("user/push_to_article.html",articles=articles,req_params=req_params)