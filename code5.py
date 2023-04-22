from bisect import bisect_left, bisect_right
from collections import defaultdict, Counter, deque
from functools import lru_cache, reduce
from heapq import heappush, heappop, heapify, heappushpop, heapreplace
import sys
from math import sqrt, gcd, factorial
#from math import isqrt, prod, comb  #python3.8用(notpypy)
import operator

#from scipy.sparse import csr_matrix
#from scipy.sparse.csgraph import shortest_path, floyd_warshall, dijkstra, bellman_ford, johnson, NegativeCycleError, maximum_bipartite_matching, maximum_flow, minimum_spanning_tree
#import networkx as nx
#from networkx.utils import UnionFind
#from numba import njit, b1, i1, i4, i8, f8
#numba例 @njit(i1(i4[:], i8[:, :]),cache=True) 引数i4配列、i8 2次元配列,戻り値i1
#import numpy as np

def input(): return sys.stdin.readline().rstrip()
def divceil(n, k): return 1+(n-1)//k  # n/kの切り上げを返す
def yn(hantei, yes='Yes', no='No'): print(yes if hantei else no)


def main():
    #mod = 10**9+7
    mod = 998244353


if __name__ == '__main__':
    main()
