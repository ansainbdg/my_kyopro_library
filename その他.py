from itertools import accumulate
import numpy as np

def group(arr, count):  # [B,A,A,C,A],A→[0,2,2,0,1]
    arr01 = list(map(lambda x: 1 if x == count else 0, arr))
    def acc(x, y): return x*y+y
    return list(map(lambda x, y: max(x+y-1, 0), accumulate(arr01, acc), list(accumulate(arr01[::-1], acc))[::-1]))

def trans(l_2d):#リストの転置
    return [list(x) for x in zip(*l_2d)]


def cross(a,b,n,mod=10**9+7):#正方行列積a@bの10**9+7modをオーバーフロー回避するために分割して掛け算する
    ans=np.zeros_like(a,dtype=np.int64)
    newn=((n//8+1)*8)
    a2=np.zeros((newn,newn),dtype=np.int64)
    a2[0:n,0:n]+=a
    b2=np.zeros((newn,newn),dtype=np.int64)
    b2[0:n,0:n]+=b
    ans=np.zeros_like(a2,dtype=np.int64)
    for k in range(newn//8):
        for i in range(newn//8):
            for j in range(newn//8):
                ans[i*8:i*8+8,j*8:j*8+8] += a2[i*8:i*8+8,k*8:k*8+8] @ b2[k*8:k*8+8,j*8:j*8+8]   
                ans[i*8:i*8+8,j*8:j*8+8] %= mod
    return ans[0:n,0:n]
