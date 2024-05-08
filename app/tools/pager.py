#!/usr/bin/env python
# -*- coding:utf-8 -*-

# from django.utils.safestring import mark_safe
from flask import Markup
from .. import app,pm,db,app_tools
_ = app_tools.BabelGetText

class PageInfo(object):
    def __init__(self, currentPage, totalItems, perItems=10, pageNum=11,path=None,ormObjs=None,open_id=False):
        try:
            currentPage = int(currentPage)
        except Exception as e:
            currentPage = 1

        self.current_page = currentPage
        self.per_items = perItems
        self.total_items = totalItems
        self.page_num = pageNum
        self.path = path
        self.orm_objs = ormObjs
        self.open_id = open_id

    @property
    def prev_count(self):
        return self.per_items * self.page_num

    @property
    def total_page(self):
        if not self.total_items:
            self.total_items = 0
        val = self.total_items / self.per_items + 1 if self.total_items % self.per_items > 0 else self.total_items / self.per_items
        return val

    @property
    def page_objs(self):
        if not self.open_id: 
            objs =  self.orm_objs[self.start : self.end] if self.orm_objs else self.orm_objs
        return objs

    @property
    def start(self):
        val = (self.current_page - 1) * self.per_items
        return val

    @property
    def end(self):
        val = self.current_page * self.per_items
        return val

    @property
    def prev_count(self):
        return (self.current_page - 1) * self.per_items

    def pager(self):
        """
        page:当前页
        all_page_count: 总页数
        """
        page_html = []
        page = self.current_page
        all_page_count = self.total_page
        total_items = self.total_items

        # 首页
        # 上一页
        if page <= 1:
            first_html = f"<li class='disabled'><a href='javascript:void(0)'>{_('首页')}</a></li>"
            prev_html = f"<li class='disabled'><a href='javascript:void(0)'>{_('上一页')}</a></li>"
        else:
            first_html = f"<li><a href='%spage=1'>{_('首页')}</a></li>" % (self.path)
            prev_html = f"<li><a href='%spage=%d'>{_('上一页')}</a></li>" % (self.path,page - 1, )
        page_html.append(first_html)
        page_html.append(prev_html)

        # 11个页码
        if all_page_count < 11:
            begin = 0
            end = all_page_count

        #总页数大于 11
        else:
            #
            if page < 6:
                begin = 0
                end = 11
            else:
                if page + 6 > all_page_count:
                    begin = page - 6
                    end = all_page_count
                else:
                    begin = page - 6
                    end = page + 5
        for i in range(int(begin), int(end)):
            #当前页
            if page == i + 1:
                #a_html = "<li class='active'><a href='%spage=%d'>%d</a></li>" % (self.path,i + 1, i + 1, )
                a_html = f"<li class='active'><a href='javascript:void(0)'>{i + 1}</a></li>"
            else:
                a_html = "<li><a href='%spage=%d' >%d</a></li>" % (self.path,i + 1, i + 1, )
            page_html.append(a_html)
        #下一页
        if page + 1 > all_page_count:
            next_html = f"<li class='disabled'><a href='javascript:void(0)'>{_('下一页')}</a></li>"
            end_html = f"<li class='disabled'><a href='javascript:void(0)' >{_('尾页')}</a></li>"
        else:
            next_html = f"<li><a href='%spage=%d' >{_('下一页')}</a></li>" % (self.path,page + 1, )
            end_html = f"<li><a href='%spage=%d' >{_('尾页')}</a></li>" % (self.path, all_page_count)

        page_html.append(next_html)
        #尾页
        # end_html = "<li><a href='javascript:void(0)' onclick='ChangePage(%d)' >尾页</a></li>" % (all_page_count, )
        page_html.append(end_html)

        # 页码概要
        end_html = f"<li><a href='javascript:;' >{_('共')} %d{_('页')} / %d {_('条数据')}</a></li>" % (all_page_count, total_items, )
        page_html.append(end_html)

        #将列表中的元素拼接成页码字符串
        page_string = Markup(''.join(page_html))

        return page_string

if __name__ == "__main__":
    """
    page_info = PageInfo(request.GET.get('page', None), pro_objs.count(),
                         path='/pro_settings/staff_pro/?search={q}&filter={filter}&select_filter={select_filter}&'.
                         format(q=get_q, filter=get_filter, select_filter=select_filter))
    """
