import numpy as np


def dot(mat1, mat2, MOD):
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
            ans = dot(ans, a, mod)
        a = dot(a, a, mod)
    return ans
