from pyecharts.charts import Kline,Line,Pie,Bar
from pyecharts import options as opts

def draw_pie(title="", node_label="",name_list=[],value_list=[]) :
    c = (
        Pie()
            .add(
            node_label,
            [list(z) for z in zip(name_list,value_list)],
            radius=["40%", "55%"],
            center=["35%", "50%"],  # 位置设置
            label_opts=opts.LabelOpts(
                position="outside",
                formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                background_color="#eee",
                border_color="#aaa",
                border_width=1,
                border_radius=4,
                rich={
                    "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                    "abg": {
                        "backgroundColor": "#e3e3e3",  # 上面的背景设置
                        "width": "100%",
                        "align": "right",
                        "height": 22,
                        "borderRadius": [4, 4, 0, 0],
                    },
                    "hr": {  # 相当于中间的分割线样式设置
                        "borderColor": "#aaa",
                        "width": "100%",
                        "borderWidth": 0.5,
                        "height": 0,
                    },
                    "b": {"fontSize": 16, "lineHeight": 33},  # 名称文字样式
                    "per": {  # 百分数的字体样式设置
                        "color": "#eee",
                        "backgroundColor": "#334455",
                        "padding": [2, 4],  # [高，宽]设置，那个背景矩形
                        "borderRadius": 2,  # 圆角设置
                    },
                },
            ),
        )
            # .set_colors(["blue", "green", "yellow", "red", "pink", "orange", "purple"]) # 颜色设置
            .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(pos_left="65%", orient="vertical"),
        )
            # .render("pie_rich_label.html")
    ).render_embed()

    return c
