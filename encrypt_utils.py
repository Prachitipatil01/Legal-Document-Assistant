from cryptography.fernet import Fernet
import os

# 🔐 Define a secure key (same key must be used for encryption and decryption)
# You can generate one using Fernet.generate_key() ONCE and reuse it
key = b'VbEeg5QdfPaQ7fYXu5kL_NBPGDWKYaJc1XKXnA2IZtI='  # Replace this with your own constant key
fernet = Fernet(key)

def encrypt_file(file_path):
    """Encrypts a file and saves it with .encrypted extension."""
    if not os.path.exists(file_path):
        print("File does not exist:", file_path)
        return

    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted_data = fernet.encrypt(data)

    encrypted_file_path = file_path + '.encrypted'
    with open(encrypted_file_path, 'wb') as f:
        f.write(encrypted_data)

    print("Encrypted file created:", encrypted_file_path)
    return encrypted_file_path  # Return path for confirmation or use

