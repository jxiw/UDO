import numpy as np

def permToInteger(perm):
    """permutation to an integer"""
    n = len(perm)
    pos = np.zeros(n)
    elems = np.zeros(n)
    k = 0
    m = 1
    for i in range(n):
        pos[i] = i
        elems[i] = i
    for i in range(n - 1):
        k += m * pos[perm[i]]
        m = m * (n - i)
        pos[elems[n - i - 1]] = pos[perm[i]]
        elems[pos[perm[i]]] = elems[n - i - 1]
    return k

def integerToPerm(n, k):
    """integer to a permutation"""
    m = k
    permuted = np.zeros(n)
    elems = np.zeros(n)
    for i in range(n):
        elems[i] = i
    for i in range(n):
        ind = m % (n - i)
        m = m / (n - i)
        permuted[i] = elems[ind]
        elems[ind] = elems[n - i - 1]
    return permuted
