from heapq import heappush, heappop, heapify, heappushpop, heapreplace
import sys
def input(): return sys.stdin.readline().rstrip()

# 通常
def main():
    v, e, r = map(int, input().split())

    graph = [[] for _ in range(v)]

    for i in range(e):
        s, t, d = map(int, input().split())
        graph[s].append((t, d))
        #graph[t].append((s, d))

    mindist = [-1] * v
    hq = []
    heappush(hq, (0, r))
    while hq:
        """ゴールが1か所だけならこれを使う
        if noad==goal:
            print(dist)
            return
        """
        dist, node = heappop(hq)
        if mindist[node] != -1:
            continue
        mindist[node] = dist
        for i, nagasa in graph[node]:
            if mindist[i] != -1:
                continue
            heappush(hq, (dist+nagasa, i))
    #print(-1) #ゴールが1か所だけならこれを使う
    for AA in mindist:
        if AA == -1:
            print('INF')
        else:
            print(AA)

# 枝刈りしてheapqに入れる値を制限ver
def main2():
    v, e, r = map(int, input().split())

    graph = [[] for _ in range(v)]

    for i in range(e):
        s, t, d = map(int, input().split())
        graph[s].append((t, d))
        #graph[t].append((s, d))

    # 距離が確定→正,距離が未確定→負
    mindist = [-10**20] * v
    hq = []
    heappush(hq, (0, r))
    while hq:
        dist, node = heappop(hq)
        """ゴールが1か所だけならこれで枝刈り
        if noad==goal:
            print(dist)
            return
        """
        if mindist[node] >= 0:  # 距離が確定済みなら飛ばす
            continue
        mindist[node] = dist  # 距離が未確定なら確定させる
        for i, nagasa in graph[node]:
            if mindist[i] >= 0:  # 距離が確定済みならhqに入れない
                continue
            if dist+nagasa >= -mindist[i]:  # 距離が暫定的にhqに入っているより大きいならhqに入れない
                continue
            heappush(hq, (dist+nagasa, i))
            mindist[i] = -dist-nagasa  # 距離が暫定距離を更新する
    
    #print(-1) #ゴールが1か所だけならこれを使う
    for AA in mindist:
        if AA == -10**20:
            print('INF')
        else:
            print(AA)


if __name__ == '__main__':
    main()
