from collections import deque
import sys
 
def input(): return sys.stdin.readline().rstrip()
 
 
def main():
    h, w = map(int, input().split())
    s = [list(input()) for i in range(h)]
    start = [0, 0]
    goal = [0, 0]
    for i in range(h):
        for j in range(w):
            if s[i][j] == 's':
                start = [i, j]
            elif s[i][j] == 'g':
                goal = [i, j]
    d = deque()
    d.append(start)
    dist = [[-1]*w for i in range(h)]
    dist[start[0]][start[1]] = 0
    while d:
        nowh, noww = d.popleft()
        for i, j in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            if ((0 <= nowh+i < h) and (0 <= noww+j < w)):
                if s[nowh+i][noww+j] != '#':
                    if dist[nowh+i][noww+j] == -1:
                        dist[nowh+i][noww+j] = dist[nowh][noww]+1
                        d.append([nowh+i, noww+j])
    if dist[goal[0]][goal[1]] != -1:
        print('Yes')
    else:
        print('No')
 
 
if __name__ == '__main__':
    main()