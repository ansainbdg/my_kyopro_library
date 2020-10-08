from networkx.utils import UnionFind
#unionfind
a, b = 1, 2
uf = UnionFind()
uf.union(a, b)  # aとbをマージ
print(uf[a] == uf[b])  # aとbが同じか判定(uf[a]はaの根を返す)
for group in uf.to_sets():  # すべてのグループのリストを返す
    pass
ap=uf.weights[a] #aが属する集合の大きさを返す

#https://qiita.com/kzm4269/items/081ff2fdb8a6b0a6112f
#https://docs.pyq.jp/python/math_opt/graph.html
import networkx as nx

#最大流、最小カット
g = nx.DiGraph()
g.add_edges_from([(0, 3, {'capacity': 10}),
                  (1, 2, {'capacity': 15})])
g.add_edge(1, 3, capacity=20)
nx.maximum_flow(g, 1, 3)
#(20, {0: {3: 0}, 3: {0: 0, 1: 0}, 1: {2: 0, 3: 20}, 2: {1: 0}})
nx.minimum_cut(g, 1, 3)
#(20, ({1, 2}, {0, 3}))

#最小費用流
G = nx.DiGraph()
G.add_node("a", demand=-5)
G.add_node("d", demand=5)
G.add_edge("a", "b", weight=3, capacity=4)
G.add_edge("a", "c", weight=6, capacity=10)
G.add_edge("b", "d", weight=1, capacity=9)
G.add_edge("c", "d", weight=2, capacity=5)
nx.min_cost_flow_cost(G)
#24
nx.min_cost_flow(G)
#{'a': {'b': 4, 'c': 1}, 'd': {}, 'b': {'d': 4}, 'c': {'d': 1}}