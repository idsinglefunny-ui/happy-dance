import hashlib
import time
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

SECRET_KEY = "dance_king_2026_secret_key"
AES_KEY = bytes.fromhex("a71d42042d0e66063fae9358fd4cdfd665a257e529e5549691cc5dc076fd9daf")
AES_IV = bytes.fromhex("01498940ea40890cad568fce8ae04763")

ALLOWED_TIME_DRIFT = 300  # 5 minutes


def make_sign(params: dict) -> str:
    """Generate MD5 sign from sorted params + timestamp + nonce + secret."""
    sorted_keys = sorted(params.keys())
    raw = ""
    for k in sorted_keys:
        raw += f"{k}={params[k]}&"
    raw += f"key={SECRET_KEY}"
    return hashlib.md5(raw.encode()).hexdigest()


def verify_sign(params: dict) -> bool:
    """Verify request signature. Returns True if valid."""
    sign = params.get("sign", "")
    t = params.get("t", "")
    nonce = params.get("nonce", "")

    if not sign or not t or not nonce:
        return False

    try:
        ts = int(t)
    except ValueError:
        return False

    if abs(time.time() - ts) > ALLOWED_TIME_DRIFT:
        return False

    # Build params without sign for verification
    check_params = {k: v for k, v in params.items() if k != "sign"}
    expected_sign = make_sign(check_params)
    return sign == expected_sign


def aes_encrypt(data: str) -> str:
    """AES-256-CBC encrypt, returns base64 string."""
    pad_len = 16 - len(data.encode()) % 16
    data_padded = data + chr(pad_len) * pad_len
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data_padded.encode()) + encryptor.finalize()
    return base64.b64encode(encrypted).decode()


def aes_decrypt(data_b64: str) -> str:
    """AES-256-CBC decrypt from base64 string."""
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(base64.b64decode(data_b64)) + decryptor.finalize()
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode()
