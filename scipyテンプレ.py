from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, floyd_warshall, dijkstra, bellman_ford, johnson, NegativeCycleError, maximum_bipartite_matching, maximum_flow, minimum_spanning_tree
import numpy as np

n, m = map(int, input().split())
edges = [list(map(int, input().split())) for i in range(m)]


def graph_csr(edges, n, directed=True, indexed_1=True):  # 隣接リストから粗行列を作成

    if len(edges[0])!=0:
        arr = np.array(edges, dtype=np.int64).T
    else:
        arr = np.zeros((3,0),dtype=np.int64)

    index = int(indexed_1)

    if arr.shape[0]==2:
        length = np.ones(len(edges),dtype=np.int64)
    elif arr.shape[0]==3:
        length = arr[2]
    else:
        raise "edge shape is 2(unweighted) or 3(weighted)"

    if not directed:
        return csr_matrix((np.concatenate([length, length]), (np.concatenate([arr[0]-index, arr[1]-index]), np.concatenate([arr[1]-index, arr[0]-index]))), shape=(n, n))
    else:
        return csr_matrix((length, (arr[0]-index, arr[1]-index)), shape=(n, n))


csr = graph_csr(edges, n)
try:
    print(floyd_warshall(csr))
except NegativeCycleError:
    print('-1')
dijkstra(csr, indices=0)
bellman_ford(csr, indices=0)
maximum_bipartite_matching(csr, perm_type='column')
maximum_flow(csr, source=0, sink=1).flow_value
maximum_flow(csr, source=0, sink=1).residual
int(sum(minimum_spanning_tree(csr).data))
