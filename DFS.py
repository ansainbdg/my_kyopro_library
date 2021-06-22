from collections import deque

n, m = map(int, input().split())

graph = [[] for _ in range(n+1)]

for i in range(m):
    a, b = map(lambda x: int(x)-1, input().split())
    graph[a].append(b)
    graph[b].append(a)

visited = [-1] * n
visited[0] = 0

d = deque()
d.append(0)

while d:
    v = d[-1]
    if graph[v] == []:  # 帰りがけ
        d.pop()
    else:  # 行きがけ
        i = graph[v].pop()
        if visited[i] != -1:
            continue
        visited[i] = 0
        d.append(i)

if visited[n] == 0:
    print('Yes')
else:
    print('No')
