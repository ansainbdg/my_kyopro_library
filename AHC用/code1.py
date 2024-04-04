# AHC用テンプレ
import sys
from math import exp, sqrt, gcd, factorial
from random import random, shuffle, choice, sample, choices, uniform, randrange, randint, seed
from time import time
# from bisect import bisect_left, bisect_right
# from collections import defaultdict, Counter, deque
# from functools import lru_cache, reduce
# from heapq import heappush, heappop, heapify, heappushpop, heapreplace
# from itertools import accumulate,permutations,combinations,combinations_with_replacement,product
# import operator


def input(): return sys.stdin.readline().rstrip()
def divceil(n, k): return 1+(n-1)//k  # n/kの切り上げを返す
def yn(hantei, yes='Yes', no='No'): print(yes if hantei else no)


def main():
    SA_start = time()
    SA_end = SA_start+1.8
    T0 = 5
    T1 = 1

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
