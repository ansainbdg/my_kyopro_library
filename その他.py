from itertools import accumulate
import numpy as np

def group(arr, count):  # [B,A,A,C,A],A→[0,2,2,0,1]
    arr01 = list(map(lambda x: 1 if x == count else 0, arr))
    def acc(x, y): return x*y+y
    return list(map(lambda x, y: max(x+y-1, 0), accumulate(arr01, acc), list(accumulate(arr01[::-1], acc))[::-1]))

def trans(l_2d):#リストの転置
    return [list(x) for x in zip(*l_2d)]


