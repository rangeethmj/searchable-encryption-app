import numpy as np
import hashlib

def encode_keyword(keyword, n, q):
    digest = hashlib.sha256(keyword.encode()).digest()
    vals = [b % q for b in digest]
    vector = (vals * ((n // len(vals)) + 1))[:n]
    return np.array(vector)