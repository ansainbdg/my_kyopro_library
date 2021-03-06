from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, floyd_warshall, dijkstra, bellman_ford, johnson, NegativeCycleError
import numpy as np

n, m = map(int, input().split())
edges = [list(map(int, input().split())) for i in range(m)]


def graph_csr(edges, n, directed=True):  # 隣接リストから粗行列を作成
    arr = np.array(edges, dtype=np.int64).T
    arr = arr.astype(np.int64)
    if not directed:
        return csr_matrix((np.concatenate([arr[2], arr[2]]), (np.concatenate([arr[0]-1, arr[1]-1]), np.concatenate([arr[1]-1, arr[0]-1]))), shape=(n, n))
    else:
        return csr_matrix((arr[2], (arr[0]-1, arr[1]-1)), shape=(n, n))


csr = graph_csr(edges, n)
try:
    print(floyd_warshall(csr))
except NegativeCycleError:
    print('-1')
dijkstra(csr, indices=0)
bellman_ford(csr, indices=0)
