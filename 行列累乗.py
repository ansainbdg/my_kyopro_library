import numpy as np
def dot(a, b, n, mod=10**9+7):  # 正方行列積a@bの10**9+7modをオーバーフロー回避するために分割して掛け算する
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
 
 
def matrix_multiplication(a, n, k, mod=10**9+7):  # n次正方行列a^k
    ans = np.eye(n, dtype=np.int64)
    while k:
        k, i = divmod(k, 2)
        if i:
            ans = dot(ans, a, n, mod)
        a = dot(a, a, n, mod)
    return ans
