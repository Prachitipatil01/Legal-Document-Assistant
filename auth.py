import bcrypt

# Dummy users (you can expand this)
users = {
    "admin": bcrypt.hashpw("password123".encode(), bcrypt.gensalt())
}

def check_login(username, password):
    if username in users:
        return bcrypt.checkpw(password.encode(), users[username])
    return False
