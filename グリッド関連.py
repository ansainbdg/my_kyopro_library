def main():#グリッドグラフを隣接リストに置き換えるテンプレート
    h, w = map(int, input().split())
    s = [list(input()) for i in range(h)]
    edges=[[] for i in range(h*w)]
    for i in range(h):
        for j in range(w):
            if s[i][j] == '#':
                continue
            if i != h-1:
                if s[i][j] == s[i+1][j]:
                    pass
            if j != w-1:
                if s[i][j] == s[i][j+1]:
                    pass

def ume(grid, fill='#'):#gridの周辺をfillで埋める関数
    result = []
    result.append([fill]*(len(grid[0])+2))
    for i in range(len(grid)):
        gyou = [fill] + grid[i] + [fill]
        result.append(gyou)

    result.append([fill]*(len(grid[0])+2))
    return result