from itertools import accumulate
import numpy as np


def group(arr, count):  # [B,A,A,C,A],A→[0,2,2,0,1]
    arr01 = list(map(lambda x: 1 if x == count else 0, arr))
    def acc(x, y): return x*y+y
    return list(map(lambda x, y: max(x+y-1, 0), accumulate(arr01, acc), list(accumulate(arr01[::-1], acc))[::-1]))


def trans(l_2d):  # リストの転置
    return [list(x) for x in zip(*l_2d)]


class Permutation_oparation:
    def __init__(self, length_or_list):
        if isinstance(length_or_list, int):
            self.permtation = list(range(length_or_list))
            self.permtation_index = list(range(length_or_list))
        else:
            self.permtation = length_or_list
            self.permtation_index = [0]*len(self.permtation)
            for i in range(len(self.permtation)):
                self.permtation_index[self.permtation[i]] = i

    def swapindex(self, a, b):  # 順列のindexである、a,bを入れ替える
        self.permtation[a], self.permtation[b] = self.permtation[b], self.permtation[a]
        self.permtation_index[a], self.permtation_index[self.permtation[b]] = self.permtation_index[self.permtation[b]], self.permtation_index[a]

    def swapitem(self, a, b):  # 順列の要素である、a,bを入れ替える
        self.permtation_index[a], self.permtation_index[b] = self.permtation_index[b], self.permtation_index[a]
        self.permtation[a], self.permtation[self.permtation_index[b]] = self.permtation[self.permtation_index[b]], self.permtation[a]

    def getitembyindex(self,a):#indexがaの要素を返す
        return self.permtation[a]
    
    def getindexbyitem(self,a):#要素aのindexを返す
        return self.permtation_index[a] 


