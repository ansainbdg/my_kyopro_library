from collections import deque

n, m = map(int, input().split())

graph = [[] for _ in range(n+1)]

for i in range(m):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

visited = [-1] * (n+1)
visited[0] = 0
visited[1] = 0

d = deque()
d.append(1)

while d:
    v = d[-1]
    if graph[v] == []:
        d.pop()
    else:
        i = graph[v].pop()
        if visited[i] != -1:
            continue
        visited[i]=0 
        d.append(i)

if visited[n]==0:
    print('Yes')
else:
    print('No')

