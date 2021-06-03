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
