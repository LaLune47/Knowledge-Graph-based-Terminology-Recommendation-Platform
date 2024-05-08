import datetime
from flask import url_for, request, Markup

def add_datetime(app):
    app.add_template_global(datetime,'datetime')

def add_strf_datetime(app):
    def strf_datetime(value,strf="%Y-%m-%d %H:%M:%S"):
        return value.strftime(strf)
    app.add_template_filter(strf_datetime,"strf_datetime")

def add_blue_url_for(app,pm):
    app.add_template_global(pm.blue_url_for, "blue_url_for")

def get_change_language(app,pm,app_tools):
    _ = app_tools.BabelGetText
    def get_local():
        lanuage = app_tools.Session.get('lang', 'en') #app_tools.Request.accept_languages.best_match(app_tools.LANGUAGES.keys())
        change_language = _("英文") if lanuage == "zh" else _("中文")
        return change_language
    app.add_template_global(get_local,"get_change_language")

def get_all_sliders(app,pm) :
    from ..user import models
    def show_sliders() :
        slider = models.SilderPic.query.order_by(models.SilderPic.order.desc()).all()
        # print("slider: ", slider)
        return slider
    app.add_template_global(show_sliders,"get_all_sliders")

def get_all_kinds(app) :
    from ..user import models
    def show_kinds() :
        kinds = models.Kinds.query.order_by(models.Kinds.order.desc()).all()
        return kinds
    app.add_template_global(show_kinds,"get_all_kinds")

def get_active_url(app,pm,app_tools):
    def get_url(name,cls="active",ch_name="",**kwargs):
        full_path = request.full_path
        name_url  = pm.blue_url_for(name,**kwargs)
        # print("name_url: ", name_url, " full_path: ", full_path)
        if str(full_path).startswith(str(name_url).rstrip("/")) :
            return name_url,cls,ch_name
        return name_url,"",ch_name

    app.add_template_global(get_url,"get_active_url")

def get_url_html(app,pm):

    html = """
        <li class="{cls}">
            <a href="{url}">
                <i class="icon-dashboard"></i>
                <span class="menu-text"> {name} </span>
            </a>
        </li>    
    """

    def get_url(name,show_name,cls="active",**kwargs):
        full_path = request.full_path
        name_url  = pm.blue_url_for(name,**kwargs)
        # print("name_url: ", name_url, " full_path: ", full_path)

        cls_status = ""
        if str(full_path).startswith(str(name_url).rstrip("/")) :
            cls_status = cls
        html_ext = html.format(cls=cls_status,url=name_url,name=show_name)
        return Markup(html_ext)
    app.add_template_global(get_url, "get_url_html")

def get_url_html_team(app,pm):
    html = """
        <li class="{cls_open}">
            <a href="javascript:;" class="dropdown-toggle">
                <i class="icon-list"></i>
                <span class="menu-text"> {menus} </span>

                <b class="arrow icon-angle-down"></b>
            </a>

            <ul class="submenu" style="{display}">
                {li_team}
            </ul>
        </li>        
    """

    html_li = """
        <li class="{cls}">
            <a href="{url}">
                <i class="icon-double-angle-right"></i>
                {name}
            </a>
        </li>
    """

    def get_url(show_name,li_args=[],cls_open="active open",cls="active",**kwargs):
        display = "display: none;"

        full_path = request.full_path

        cls_open_status = ""
        display_status = display
        html_lis = ""
        for li in li_args :
            name_url  = pm.blue_url_for(li["name"],**li.get("args",{}))
            # print("name_url: ", name_url, " full_path: ", full_path)

            cls_status = ""
            if str(full_path).startswith(str(name_url).rstrip("/")) :
                cls_status = cls
                cls_open_status = cls_open
                display_status = ""
            html_lis += html_li.format(cls=cls_status,url=name_url,name=li["show_name"])
        html_ext = html.format(cls_open=cls_open_status,menus=show_name,display=display_status,li_team=html_lis)
        return Markup(html_ext)
    app.add_template_global(get_url, "get_url_html_team")

def get_user_cards(app,pm,app_tools):
    def user_cards() :
        from ..user import models
        from flask_login import current_user
        nums = 0

        try:
            cards = models.Cards.query.filter_by(user_id=current_user.id, pay_status=False)
            for tmp_card in cards :
                nums += 1
        except Exception as e :
            pass
        return nums
    app.add_template_global(user_cards,"get_user_cards")

def add_template(app,pm,app_tools):
    add_datetime(app)
    add_strf_datetime(app)
    add_blue_url_for(app,pm)
    get_change_language(app,pm,app_tools)
    get_all_sliders(app, pm)
    get_all_kinds(app)

    get_active_url(app,pm,app_tools)
    get_url_html(app,pm)
    get_url_html_team(app,pm)

    get_user_cards(app,pm,app_tools)
