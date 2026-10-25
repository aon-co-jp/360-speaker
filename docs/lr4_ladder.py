"""LR4(4次Linkwitz-Riley)受動ラダーの正規化素子値(R=1, w=1)を数値で求める。"""
import math

def padd(a, b):
    n = max(len(a), len(b)); return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]
def pmul(a, b):
    r = [0.0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i + j] += x * y
    return r
def mm(X, Y):
    return [[padd(pmul(X[i][0], Y[0][j]), pmul(X[i][1], Y[1][j])) for j in range(2)] for i in range(2)]

def ladder(g):
    L1, C1, L2, C2 = g
    T = [[[1], [0, L1]], [[0], [1]]]
    for m in ([[[1], [0]], [[0, C1], [1]]], [[[1], [0, L2]], [[0], [1]]], [[[1], [0]], [[0, C2], [1]]]):
        T = mm(T, m)
    D = padd(T[0][0], T[0][1]); return D + [0.0] * (5 - len(D))

def solve(A, b):
    n = len(b); M = [A[i][:] + [b[i]] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]; M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [M[i][n] / M[i][i] for i in range(n)]

def lr4_lp_g():
    q = [1, math.sqrt(2), 1]; tgt = pmul(q, q)
    g = [1.0, 1.0, 1.0, 1.0]
    for _ in range(200):
        d0 = ladder(g); r = [d0[k] - tgt[k] for k in range(1, 5)]
        if sum(x * x for x in r) < 1e-22: break
        J = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            h = [0.0] * 4; h[i] = 1e-6
            a, b = ladder([x + y for x, y in zip(g, h)]), ladder([x - y for x, y in zip(g, h)])
            for k in range(4): J[k][i] = (a[k + 1] - b[k + 1]) / 2e-6
        st = solve(J, r); g = [x - y for x, y in zip(g, st)]
    return g

if __name__ == "__main__":
    g = lr4_lp_g(); print(g, [round(x, 5) for x in ladder(g)])
