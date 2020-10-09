import heapq
import sys
def input(): return sys.stdin.readline().rstrip()


v, e, r = map(int, input().split())

graph = [[] for _ in range(v)]

for i in range(e):
    s, t, d = map(int, input().split())
    graph[s].append((t, d))
    #graph[t].append((s, d))

mindist = [-1] * v
hq = []
heapq.heappush(hq, (0, r))
while hq:
    dist, node = heapq.heappop(hq)
    if mindist[node] != -1:
        continue
    mindist[node]=dist
    for i,nagasa in graph[node]:
        if mindist[i] != -1:
            continue
        heapq.heappush(hq, (dist+nagasa, i))

for AA in mindist:
    if AA==-1:
        print('INF')
    else:
        print(AA)
