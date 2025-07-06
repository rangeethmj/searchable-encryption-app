import numpy as np

n = 64
q = 3329
sigma = 2

def generate_matrix_A(n=n, q=q):
    A = np.random.randint(0, q, size=(n, n))
    return A

def get_params():
    return {
        "n": n,
        "q": q,
        "sigma": sigma
    }