# AHC用テンプレ
import sys
from math import exp
from random import random,shuffle,choice,sample,choices,uniform,randrange
from time import time

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
    start_time=time()
    SA_start=time()
    SA_end=start_time+1.8
    T0=5
    T1=1
    
    def get_temp(Time):
        return T0+(Time-SA_start)*(T0-T1)/(SA_start-SA_end)
    
    """
    while True:
        i += 1
        now_time=time.time()
        if now_time>SA_end:
           break
        temp = get_temp(now_time)
        delta = 
        if delta > 0 or random.random()<exp(delta/temp):
            pass
        else:
    """


if __name__ == '__main__':
    main()
