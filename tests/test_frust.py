import numpy as np
import time
from math import comb

def get_frustration(matrix):
    N, D = matrix.shape
    if N < 3: return 0.0
    ranks = np.argsort(np.argsort(matrix, axis=0), axis=0)
    ranks_noisy = ranks + np.random.normal(0, 1e-6, size=ranks.shape)
    C = np.corrcoef(ranks_noisy, rowvar=False)
    A = np.sign(C)
    np.fill_diagonal(A, 0)
    A2 = np.dot(A, A)
    A3 = np.dot(A2, A)
    T_total = comb(D, 3)
    T_frust = 0.5 * (T_total - np.trace(A3) / 6.0)
    return T_frust / T_total

t0 = time.time()
mat = np.random.randn(23, 768)
frust = get_frustration(mat)
t1 = time.time()
print(f"23 nodes: Frustration={frust:.4f}, Time={t1-t0:.4f}s")

t0 = time.time()
mat = np.random.randn(500, 768)
frust = get_frustration(mat)
t1 = time.time()
print(f"500 nodes: Frustration={frust:.4f}, Time={t1-t0:.4f}s")
