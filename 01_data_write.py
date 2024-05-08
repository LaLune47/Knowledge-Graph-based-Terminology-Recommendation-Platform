import os
from app import app as apps,db,app_tools
from app.user import models
from app.tools.neo4j_handler import graph_handler

from py2neo import Graph, Node, Relationship

db.create_all()

class NodeObj:
    def __init__(self, label="", name="", property={}):
        self.node = Node(label, name=name, **property)
        self.label = label
        self.name = name
        self.property = property

class RelObj:
    def __init__(self, node1: NodeObj, name, node2: NodeObj, property={}):
        self.node1 = node1
        self.node2 = node2
        self.name = name
        self.property = property

graph_handler.clear_db()

def write_db():
    path = r"D:\Programmer\ProgrammerPersionWrok\Python\185_flask_新闻文章分类分析处理\programmer\analyze\training"
    models.ArticleDetails.query.delete()
    db.session.commit()

    map_choices = {}
    for k, v in models.KIND_ARTICLE_CHOICES:
        map_choices[k] = v

    node_lis = []
    rel_lis = []
    data_lis = []
    for f in os.listdir(path):
        fpath = os.path.join(path, f)
        f_kind = f.split("_")[0]
        f_kind = int(f_kind)

        with open(fpath, "r", encoding="utf-8") as ff:
            data = ff.read()
        data = str(data).strip()


        title = data[:16]

        try:
            map_choices[str(f_kind)]
        except Exception:
            continue

        data_lis.append({
            "title": title,
            "content": data,
            "user_id": 0,
            "kind": f_kind,
        })

    db.session.bulk_insert_mappings(models.ArticleDetails, data_lis)
    db.session.commit()

    for obj in models.ArticleDetails.query.all():
        NodeOne = NodeObj("类别", name=map_choices[str(obj.kind)], property={"nid": obj.kind})
        NodeTwo = NodeObj("文章", name=obj.title, property={"content": data, "nid": obj.id})
        node_lis.append(NodeOne)
        node_lis.append(NodeTwo)
        rel_lis.append(RelObj(NodeOne, "类别", NodeTwo))

    tx = graph_handler.graph.begin()
    for node in node_lis:
        tx.merge(node.node, node.label, "name")
    tx.commit()

    tx = graph_handler.graph.begin()
    for rel in rel_lis:
        tx.create(Relationship(rel.node1.node, rel.name, rel.node2.node, **rel.property))
    tx.commit()

if __name__ == "__main__":
    write_db()