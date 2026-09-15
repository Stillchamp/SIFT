import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

SECRET_KEY = "Officer_123"
enc_filename = "AES_ENC_d_DE_97dec79a (1).enc" # Replace with your actual filename

# 1. DECRYPT THE FILE
with open(enc_filename, "rb") as f:
    ciphertext = f.read()

key = SECRET_KEY.encode('utf-8').ljust(32, b'\0')[:32]
iv = ciphertext[:16]
actual_ciphertext = ciphertext[16:]

cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
decryptor = cipher.decryptor()
padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()

unpadder = padding.PKCS7(128).unpadder()
plain_bytes = unpadder.update(padded_data) + unpadder.finalize()

# Save as readable plaintext so you can open and edit it
with open("editable_evidence.txt", "wb") as f:
    f.write(plain_bytes)

print("[+] File decrypted successfully as 'editable_evidence.txt'. Open it, change a letter, and save.")

input("Press Enter AFTER you have edited and saved 'editable_evidence.txt' to re-encrypt it...")

# 2. RE-ENCRYPT THE ALTERED FILE
with open("editable_evidence.txt", "rb") as f:
    new_plain_bytes = f.read()

new_iv = os.urandom(16)
padder = padding.PKCS7(128).padder()
new_padded = padder.update(new_plain_bytes) + padder.finalize()

encryptor = cipher.encryptor() # Reusing AES setup
# Wait, need a fresh encryptor with the new IV:
new_cipher = Cipher(algorithms.AES(key), modes.CBC(new_iv), backend=default_backend())
new_encryptor = new_cipher.encryptor()
new_ciphertext = new_iv + new_encryptor.update(new_padded) + new_encryptor.finalize()

with open("tampered_working_copy.enc", "wb") as f:
    f.write(new_ciphertext)

print("[+] Tampered file re-encrypted as 'tampered_working_copy.enc'.")
print("[+] Upload this file during the Check-In step to trigger the spoliation alert!")