from urllib.parse import urlencode,parse_qs,urlparse

#show_data,show_page = page(data=[], all_count=80, cur_page=request.GET.get("page"),request=request.path,params=request.build_absolute_uri())
def page(data=[], half_count=5, all_count=0,
         page_count=20, cur_page=-1,base_url="",params={},
         page_code="page",cur_page_status="current",
         request=None
         ):
    if request:
        base_url = request.path if not base_url else base_url
        params = request.full_path if not params else params
        cur_page = request.args.get(page_code,"page") if cur_page == -1 else cur_page

    def cur_href(base_url,params,cur_count_page,all_page=-1):
        if cur_count_page == cur_page:
            return "javascript:;"
        if cur_count_page <= 0:
            return "javascript:;"
        if all_page != -1 and cur_count_page >= all_page:
            return "javascript:;"
        if type(params) == str:
            query = urlparse(params).query
            params = {k:v[0] for k,v in parse_qs(query).items()}
        if page_code:
            params[page_code] = cur_count_page
        url_params = urlencode(params)
        if "?" in base_url:
            base_url += "&" + url_params
        else:
            base_url += "?" + url_params
        return base_url

    def get_current(cur_page,page):
        if cur_page == page:
            return cur_page_status
        return ""

    def get_num(page):
        return f"""&nbsp;{page}&nbsp;"""

    span_href = ""

    if all_count == 0:
        try:
            all_count = len(data)
        except Exception as e :
            all_count = data.count()

    try:
        cur_page = int(cur_page)
    except Exception as e:
        cur_page = 1

    if cur_page == 1:
        span_href += """<span class="unprev"></span>"""
    else:
        span_href += f"""<a href="{cur_href(base_url,params,cur_page-1)}" class="prev"></a>"""

    l, r = divmod(all_count, page_count)
    if r != 0:
        l += 1

    if cur_page > l:
        cur_page = l
    elif cur_page < 1:
        cur_page = 1

    if l > half_count * 2:
        if cur_page <= half_count:
            for count in range(1, half_count + 1 + cur_page):
                span_href += f"""<a href="{cur_href(base_url,params,count)}" class="{get_current(cur_page,count)}">{get_num(count)}</a>"""

            if cur_page+half_count+1 != l:
                span_href += """<span class="etc"></span>"""
                span_href += f"""<a href="{cur_href(base_url,params,l)}" >{get_num(l)}</a>"""
        elif cur_page >= l - half_count:
            if l - half_count - 1 != 1:
                span_href += f"""<a href="{cur_href(base_url,params,1)}" >{get_num(1)}</a>"""
                span_href += """<span class="etc"></span>"""

            for count in range(cur_page - half_count, l + 1):
                span_href += f"""<a href="{cur_href(base_url,params,count)}" class="{get_current(cur_page,count)}">{get_num(count)}</a>"""
        else:
            if cur_page - half_count != 1:
                span_href += f"""<a href="{cur_href(base_url,params,1)}" >{get_num(1)}</a>"""
                span_href += """<span class="etc"></span>"""
            for count in range(cur_page - half_count,cur_page+half_count+1):
                span_href += f"""<a href="{cur_href(base_url,params,count)}" class="{get_current(cur_page,count)}">{get_num(count)}</a>"""
            if cur_page+half_count+1 != l:
                span_href += """<span class="etc"></span>"""
                span_href += f"""<a href="{cur_href(base_url,params,l)}" >{get_num(l)}</a>"""
    else:
        for count in range(1,l+1):
            span_href += f"""<a href="{cur_href(base_url,params,count)}" class="{get_current(cur_page,count)}">{get_num(count)}</a>"""

    if cur_page == l:
        span_href += """<span class="unnext"></span>"""
    else:
        span_href += f"""<a href="{cur_href(base_url,params,cur_page+1,all_page=l)}" class="next"></a>"""

    # print(span_href)

    span_href = f"""<div id="page" class="page" style="display:block;"><div class="page_num">{span_href}</div></div>"""

    if all_count == 0:
        return 0,0,span_href
    return (cur_page - 1) * page_count,cur_page * page_count,span_href

if __name__ == "__main__":
    page(data=[], all_count=580,cur_page=12)