import numpy as np


def hakidashi(A):
    AA = np.sort(A)[::-1]
    ans = []
    while AA.shape[0] and AA[0]:
        ans.append(AA[0])
        AA[np.where(AA ^ AA[0] < AA)[0]] ^= AA[0]
        AA = np.sort(AA)[::-1]
    return np.array(ans)


def highest_bit(v):
    """
    Vの最上位ビットのみを残した値を作る。
    """
    v = v | (v >> 1)
    v = v | (v >> 2)
    v = v | (v >> 4)
    v = v | (v >> 8)
    v = v | (v >> 16)
    v = v | (v >> 32)
    return v ^ (v >> 1)


def hakidashi_hantei(ans, K):
    for aa in ans:
        if highest_bit(aa) & K:
            K ^= aa
    return K == 0

def hakidashi2(A):
    x,y=A.shape
    ans = []
    for i in range(y):
        if A[:,i].max() != 0:
            A=A[np.argsort(A[:,i])[::-1]]
            ans.append(np.copy(A[0]))
            #print(A)
            A[np.where(A[:,i]>0)[0]]^=A[0]
    return np.stack(ans)
 
def hakidashi_hantei2(ans, K):
    for aa in ans:
        if K[np.where(aa==1)[0][0]]!=0:
            K ^= aa
    return np.all(K == np.zeros_like(K))