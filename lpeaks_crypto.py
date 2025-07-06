import numpy as np
import hashlib
from setup import generate_matrix_A, get_params
from utils import encode_keyword
from datetime import datetime

def setup():
    pp = {
        "A": generate_matrix_A(),
        "params": get_params()
    }
    MSK = np.random.randint(0, pp["params"]["q"], size=pp["params"]["n"])
    return pp, MSK

def keygen(pp, MSK, identity):
    n, q = pp["params"]["n"], pp["params"]["q"]
    h = hashlib.sha256(identity.encode()).digest()
    id_vec = np.array([b % q for b in h] * ((n // len(h)) + 1))[:n]
    sk = (MSK + id_vec) % q
    return sk

def authorize(pp, skID, keyword, timestamp):
    kw_vec = encode_keyword(keyword, pp["params"]["n"], pp["params"]["q"])
    time_hash = hashlib.sha256(timestamp.encode()).digest()
    t_vec = np.array([b % pp["params"]["q"] for b in time_hash] * ((pp["params"]["n"] // len(time_hash)) + 1))[:pp["params"]["n"]]
    token = (skID + kw_vec + t_vec) % pp["params"]["q"]
    return token

def encrypt(pp, ID, keyword):
    n, q = pp["params"]["n"], pp["params"]["q"]
    A = pp["A"]
    kw_vec = encode_keyword(keyword, n, q)
    s = np.random.randint(0, q, size=n)
    e = np.random.randint(-2, 3, size=n)
    CT = (A @ s + kw_vec + e) % q
    return CT

def trapdoor(pp, ID, token, keyword):
    # ✅ FIXED: Don't add kw_vec again
    return token

def test(pp, ID, CT, TRAP, current_time_str, authorized_until=None):
    q = pp["params"]["q"]

    # Optional: validate time-based authorization
    if authorized_until:
        try:
            now = datetime.fromisoformat(current_time_str)
            expire = datetime.fromisoformat(authorized_until)
            if now > expire:
                return False  # Authorization expired
        except:
            pass  # If format is invalid, ignore time check

    diff = (CT - TRAP) % q
    diff = np.where(diff > q // 2, diff - q, diff)  # Center around 0
    return np.all(np.abs(diff) <= 10)
