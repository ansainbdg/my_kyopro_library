def permutation(n, r, mod=10**9+7):  # 順列数
    permutation = 1
    for i in range(r):
        permutation = permutation*(n-i) % mod
    return permutation


def combination(n, r, mod=10**9+7):  # 組み合わせ数
    r = min(n-r, r)
    bunshi = permutation(n, r, mod)
    bunbo = 1
    for i in range(1, r+1):
        bunbo = bunbo*i % mod
    return bunshi*pow(bunbo, mod-2, mod) % mod


def combination_with_repetition(n, r, mod=10**9+7):  # n種類からr個取る重複組み合わせ数
    return combination(n+r-1, mod-2, mod)



class PrepereFactorial:  # maxnumまでの階乗を事前計算して、順列、組み合わせ、重複組み合わせを計算するクラス
    def __init__(self, maxnum=3*10**5, mod=10**9+7):
        self.factorial = [1]*(maxnum+1)
        for i in range(1, maxnum+1):
            self.factorial[i] = (self.factorial[i-1]*i) % mod
        self.mod = mod

    def permutation(self, n, r):
        return (self.factorial[n]*pow(self.factorial[n-r], self.mod-2, self.mod)) % self.mod

    def combination(self, n, r):
        return self.permutation(n, r)*pow(self.factorial[r], self.mod-2, self.mod) % self.mod
    def combination_with_repetition(self, n, r):
        return self.combination(n+r-1, r)
