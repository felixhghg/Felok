import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Felok.key")

def _get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
            if len(key) == 32:
                return key
    key = get_random_bytes(32)
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

_MASTER_KEY = _get_or_create_key()

def encrypt_data(plaintext: str) -> bytes:
    if not plaintext:
        return b""
    cipher = AES.new(_MASTER_KEY, AES.MODE_GCM, nonce=get_random_bytes(12))
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    return cipher.nonce + tag + ciphertext

def decrypt_data(blob: bytes) -> str:
    if not blob or len(blob) < 28:
        return ""
    try:
        nonce = blob[:12]
        tag = blob[12:28]
        ciphertext = blob[28:]
        cipher = AES.new(_MASTER_KEY, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except Exception as e:
        raise e
