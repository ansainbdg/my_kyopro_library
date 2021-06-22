from collections import deque
from copy import deepcopy


def main():
    """
    グラフが隣接辺で与えられる場合
    """
    mod = 10**9+7
    mod2 = 998244353
    n = int(input())

    graph = [[] for _ in range(n)]

    for i in range(n-1):
        a, b = map(lambda x: int(x)-1, input().split())
        graph[a].append(b)
        graph[b].append(a)

    mother = [[] for _ in range(n)]
    dp = [1]*n
    # print(dp)
    visited = [False]*n
    visited[0] = True

    d = deque()
    d.append(0)

    def merge(a, b):
        return (a*b) % mod

    while d:
        v = d[-1]
        if graph[v] == []:  # 帰りがけ
            for m in mother[v]:
                dp[v] = merge(dp[v], dp[m])
            d.pop()
        else:  # 行きがけ
            i = graph[v].pop()
            if visited[i]:
                continue
            visited[i] = True
            d.append(i)
            mother[v].append(i)
    print(dp[0])


def main2():
    """
    グラフが親リストで与えられる場合
    """
    mod = 10**9+7
    mod2 = 998244353
    n = int(input())
    A = list(map(lambda x: int(x)-1, input().split()))
    mothers = [[] for i in range(n)]
    for i, AA in enumerate(A, 1):
        mothers[AA].append(i)
    m2 = deepcopy(mothers)
    d = deque()
    d.append(0)
    def merge(a, b):
        return (a*b) % mod
    while d:
        v = d[-1]
        if m2[v] == []:
            d.pop()
            for m in mothers[v]:
                dp[v]=merge(dp[v],dp[m])
        else:
            i = m2[v].pop()
            d.append(i)
    print(dp[0])
