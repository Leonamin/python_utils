

import hashlib
import os

# 사용자 비밀번호
password = 'dca486298VJ'

# 안전하게 Salt 생성 (여기서는 16바이트 사용)
salt = 'fd8f28f059ed964f'

# 비밀번호와 Salt를 결합
password_salt = password.encode() + salt.encode()

# SHA-256을 사용해 해싱
hash_object = hashlib.sha256(password_salt)
hashed_password = hash_object.hexdigest()

print("Salted and hashed password:", hashed_password)
