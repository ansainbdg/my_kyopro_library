def main():
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
