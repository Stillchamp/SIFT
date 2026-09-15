from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def encrypt_data(plain_text: bytes, secret_key: str) -> bytes:
    """Encrypts byte data using AES-256 in CBC mode, mirroring the thesis requirements."""
    # Ensure key is exactly 32 bytes for AES-256
    key = secret_key.encode('utf-8').ljust(32, b'\0')[:32]
    iv = os.urandom(16)
    
    # Pad data to block size (128 bits / 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text) + padder.finalize()
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = iv + encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext

def decrypt_data(ciphertext: bytes, secret_key: str) -> bytes:
    """Decrypts AES-256 encrypted byte data."""
    key = secret_key.encode('utf-8').ljust(32, b'\0')[:32]
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()
    
    # Unpad data
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data