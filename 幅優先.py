from collections import deque
    
def main():
    n, m = map(int, input().split())
    
    graph = [[] for _ in range(n)]
    
    for i in range(m):
        a, b = map(lambda x: int(x)-1, input().split())
        graph[a].append(b)
        graph[b].append(a)
    
    dist = [-1] * (n+1)
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