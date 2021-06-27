import sys
import os
import numpy as np

def solve(n):
    su = 0
    for i in range(1, n+1):
        m = n//i
        su += m*(2*i + (m-1)*i)//2
    return su

SIGNATURE = 'i8(i8)'
if sys.argv[-1] == 'ONLINE_JUDGE':
    from numba.pycc import CC
 
    cc = CC('my_module')
    cc.export('solve', SIGNATURE)(solve)
    cc.compile()
    exit()
    
if os.name == 'posix':
    # noinspection PyUnresolvedReferences
    from my_module import solve
else:
    from numba import njit
 
    solve = njit(SIGNATURE, cache=True)(solve)
    print('compiled', file=sys.stderr)

n=int(input())    
print(solve(n))