import sys
 
def solve(n):
    return n
 
if sys.argv[-1] == 'ONLINE_JUDGE':
    from numba.pycc import CC
 
    cc = CC('my_module')
    cc.export('solve', 'i8(i8)')(solve)
    cc.compile()
    exit()
    
n=int(input())    
print(solve(n))