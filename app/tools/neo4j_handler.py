from py2neo import Graph,Node,Relationship,NodeMatcher, Subgraph
from py2neo.bulk import create_nodes, merge_nodes, create_relationships, merge_relationships
from .. import settings

import time
class Neo4j_Handle():
    graph = None
    def __init__(self):
        print("Neo4j Init ...")
        while True:
            try:
                self.graph = Graph(settings.GRAPH_URL, name="neo4j", auth=(settings.GRAPH_USERNAME, settings.GRAPH_PASSWORD))
                print("Neo4j Success ...")
                break
            except Exception as e:
                print("Neo4j Error ...")
                # 等待 5s
                time.sleep(5)


    def clear_db(self):
        sql = "MATCH (n) DETACH DELETE n"
        self.graph.run(sql)

    #实体查询
    def matchEntityItem(self):
        sql = "MATCH (entity1)  RETURN entity1"
        print(sql)
        answer = self.graph.run(sql).data()
        return answer

    def batch_create(self, nodes_list, relations_list):
        """
            批量创建节点/关系,nodes_list和relations_list不同时为空即可
            特别的：当利用关系创建节点时，可使得nodes_list=[]
        :param graph: Graph()
        :param nodes_list: Node()集合
        :param relations_list: Relationship集合
        :return:
        """

        subgraph = Subgraph(nodes_list, relations_list)
        tx_ = self.graph.begin()
        tx_.create(subgraph)
        # tx_.merge(subgraph)
        self.graph.commit(tx_)

graph_handler = Neo4j_Handle()