V, E = map(int, input().split())
cost = [[float("inf")]*V for i in range(V)]
for i in range(E):
    s, t, d = map(int, input().split())
    cost[s][t] = d
for i in range(V):
    cost[i][i] = 0

for k in range(V):
    for i in range(V):
        for j in range(V):
            cost[i][j] = min(cost[i][j], cost[i][k] + cost[k][j])
if any(cost[i][i] < 0 for i in range(V)):
    print("NEGATIVE CYCLE")
else:
    for costs in cost:
        print(*['INF' if x==float('inf') else x for x in costs])