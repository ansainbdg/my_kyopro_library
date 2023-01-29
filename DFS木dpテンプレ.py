from collections import deque

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

    dp = [1]*n

    d = deque()
    now = set()
    d.append(~0)
    d.append(0)

    def merge(a, b):
        return (a*b) % mod
    
    while d:
        i = d.pop()
        now.add(i)
        if i >= 0:# 行きがけ
            for j in graph[i]:
                if j  not in now:
                    d.append(~j)
                    d.append(j)
        else:  # 帰りがけ
            i=~i
            now.discard(i)
            for j in graph[i]:
                if j not in now:
                    dp[i] = merge(dp[i], dp[j])
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

    dp = [1]*n
    d = deque()
    d.append(~0)
    d.append(0)
    def merge(a, b):
        return (a*b) % mod
    while d:
        i = d.pop()
        if i >= 0:# 行きがけ
            for j in mothers[i]:
                d.append(~j)
                d.append(j)
        else:  # 帰りがけ
            i=~i
            for j in mothers[i]:
                dp[i] = merge(dp[i], dp[j])
    print(dp[0])
