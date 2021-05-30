from itertools import accumulate


class accmulate2d():
    def __init__(self, A):
        self.acc = [[0]*(len(A[0])+1)]
        self.acc.extend([[0]+list(accumulate(AA)) for AA in A])
        for i in range(1, len(self.acc)):
            self.acc[i] = [self.acc[i-1][j]+self.acc[i][j]
                           for j in range(len(self.acc[0]))]

    def query(self, x2, y2, x1=1, y1=1):
        """
        1_indexed
        """
        return self.acc[x2][y2]-self.acc[x2][y1-1]-self.acc[x1-1][y2]+self.acc[x1-1][y1-1]
