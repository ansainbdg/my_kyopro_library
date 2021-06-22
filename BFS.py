from collections import deque


def main():
    n, m = map(int, input().split())

    graph = [[] for _ in range(n)]

    for i in range(m):
        a, b = map(lambda x: int(x)-1, input().split())
        graph[a].append(b)
        graph[b].append(a)

    dist = [-1] * n
    dist[0] = 0

    d = deque()
    d.append(0)

    while d:
        v = d.popleft()
        for i in graph[v]:
            if dist[i] != -1:
                continue
            dist[i] = dist[v] + 1
            d.append(i)

    print(*dist, sep="\n")


def BFS01():
    n, m = map(int, input().split())

    graph0 = [[] for _ in range(n)]
    graph1 = [[] for _ in range(n)]
    for i in range(m):
        a, b, c = map(lambda x: int(x)-1, input().split())
        if c+1 == 1:
            graph1[a].append(b)
            graph1[b].append(a)
        else:
            graph0[a].append(b)
            graph0[b].append(a)

    dist = [10**10] * n
    dist[0] = 0

    d = deque()
    d.append(0)

    while d:
        v = d.popleft()
        for i in graph0[v]:
            if dist[i] <= dist[v]:
                continue
            dist[i] = dist[v]
            d.appendleft(i)
        for i in graph1[v]:
            if dist[i] <= dist[v]+1:
                continue
            dist[i] = dist[v] + 1
            d.append(i)

    print(*dist, sep="\n")
