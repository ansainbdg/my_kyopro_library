from collections import defaultdict
# https://note.nkmk.me/python-union-find/から一部改変


class UnionFind():
    def __init__(self, n):
        self.n = n
        self.parents = [-1] * n
        self.group_num = n

    def find(self, x):
        if self.parents[x] < 0:
            return x
        else:
            self.parents[x] = self.find(self.parents[x])
            return self.parents[x]

    def union(self, x, y):
        x = self.find(x)
        y = self.find(y)

        if x == y:
            return

        self.group_num -= 1
        if self.parents[x] > self.parents[y]:
            x, y = y, x

        self.parents[x] += self.parents[y]
        self.parents[y] = x

    def size(self, x):
        return -self.parents[self.find(x)]

    def same(self, x, y):
        return self.find(x) == self.find(y)

    def members(self, x):
        root = self.find(x)
        return [i for i in range(self.n) if self.find(i) == root]

    def roots(self):
        return [i for i, x in enumerate(self.parents) if x < 0]

    def group_count(self):
        return self.group_num

    def all_group_members(self):
        self.all_group_member = defaultdict(list)
        for i in range(self.n):
            self.all_group_member[self.find(i)].append(i)
        return self.all_group_member

    def __str__(self):
        return '\n'.join('{}: {}'.format(r, self.members(r)) for r in self.roots())
