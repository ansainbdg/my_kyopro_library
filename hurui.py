#N以下の数字の素因数分解を返す　2~3*10**6が2sec範囲
def hurui(N):
    factor = [i for i in range(N+1)]
    factorize = [None] * (N+1)
    factorize[1] = dict()
    for i in range(2,N+1):
        if factor[i]==i:
            for j in range(2*i,N+1,i):
                factor[j]=i
        factorize[i] = factorize[i//factor[i]].copy()
        if factor[i] in factorize[i]:
            factorize[i][factor[i]]+=1
        else:
            factorize[i][factor[i]]=1
    return factorize