n, w, r = [int(x) for x in input().split()]  # n:頂点数, w:辺の数
g = []
for _ in range(w):
    x, y, z = [int(x) for x in input().split()]  # 始点,終点,コスト
    g.append([x, y, z])
    # g.append([y, x, z])  # 有向グラフでは削除

d = [float('inf')]*n  # 各頂点への最小コスト
d[r] = 0  # 自身への距離は0
for i in range(n):
    update = False  # 更新が行われたか
    for x, y, z in g:
        if d[y] > d[x] + z:
            d[y] = d[x] + z
            update = True
    if not update:
        break
    # 負閉路が存在
    if i == n - 1:
        print("NEGATIVE CYCLE")
print(*['INF' if x==float('inf') else x for x in d],sep='\n')
