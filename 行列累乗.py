import numpy as np


def dot(a, b, n, mod=10**9+7): 
    """
    正方行列積a@bの10**9+7modをオーバーフロー回避するために分割して掛け算する
    """
    ans = np.zeros_like(a, dtype=np.int64)
    newn = ((n//8+1)*8)
    a2 = np.zeros((newn, newn), dtype=np.int64)
    a2[0:n, 0:n] += a
    b2 = np.zeros((newn, newn), dtype=np.int64)
    b2[0:n, 0:n] += b
    ans = np.zeros_like(a2, dtype=np.int64)
    for k in range(newn//8):
        for i in range(newn//8):
            for j in range(newn//8):
                ans[i*8:i*8+8, j*8:j*8+8] += a2[i*8:i*8+8,
                                                k*8:k*8+8] @ b2[k*8:k*8+8, j*8:j*8+8]
                ans[i*8:i*8+8, j*8:j*8+8] %= mod
    return ans[0:n, 0:n]


def dot2(mat1, mat2, MOD):
    """
    行列積a@bの10**9+7modをオーバーフロー回避するために上下15bitで分割して掛け算する 
    https://ikatakos.com/pot/programming_algorithm/python_tips/avoid_overflow
    """
    mask = (1 << 15) - 1
    mat1h = mat1 >> 15
    mat1l = mat1 & mask
    mat2h = mat2 >> 15
    mat2l = mat2 & mask
    mathh = mat1h @ mat2h % MOD
    matll = mat1l @ mat2l % MOD
    mathl = (mathh + matll - (mat1h - mat1l) @ (mat2h - mat2l)) % MOD
    res = (mathh << 30) + (mathl << 15) + matll
    res %= MOD
    return res


def matrix_multiplication(a, n, k, mod=10**9+7):  # n次正方行列a^k
    ans = np.eye(n, dtype=np.int64)
    while k:
        k, i = divmod(k, 2)
        if i:
            ans = dot2(ans, a, mod)
        a = dot2(a, a, mod)
    return ans
