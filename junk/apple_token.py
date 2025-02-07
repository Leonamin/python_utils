import jwt
import time
from datetime import datetime, timedelta
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# apple_private_key = """-----BEGIN PRIVATE KEY-----
# MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgD9owgtfnWuWQxjud
# WuiZfV5Ts8J0QTvZILrKxhHX8tCgCgYIKoZIzj0DAQehRANCAATph+RmQ8ZMdfgD
# XnQaQqQ5sN0YjBaJRjnvPcpx3uk5COcsViJf68Q+1a+adD8l+h84giz2iAJOyMhc
# S0QBwZQ6
# -----END PRIVATE KEY-----"""
# apple_kid = "GJ48YS7C6U"
# apple_iss = "74RA7Q97YK"
apple_private_key = """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgAOad83Y98s+fE3BM
KgBnvlKibbAVG6433/LT1tlvgmWgCgYIKoZIzj0DAQehRANCAAS8fxf0pSf+2iag
aVvgz21gUAdSBakmv0vH0/EDnmBGkZCt3rw5MTK2bjbs0JzeUO4SrT5Pj0ZPE7p/
lPAtm+/z
-----END PRIVATE KEY-----"""
apple_kid = "58KC7J8L3S"
apple_iss = "74RA7Q97YK"
apple_sub = "io.lokks.careease.debug"


def get_apple_token_info(apple_code):

    # 개인 키 로드
    priv_key = serialization.load_pem_private_key(
        apple_private_key.encode(),
        password=None,
        backend=default_backend()
    )

    # 현재 시간 및 만료 시간 설정
    now = datetime.utcnow()
    exp = now + timedelta(hours=32)

    # JWT 토큰 생성
    token = jwt.encode(
        {
            "iss": apple_iss,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "aud": "https://appleid.apple.com",
            "sub": apple_sub,
        },
        priv_key,
        algorithm='ES256',
        headers={"kid": apple_kid}
    )

    print(token)

    url = "https://appleid.apple.com/auth/token"
    body_data = {
        "client_id": apple_sub,
        "client_secret": token,
        "code": apple_code,
        "grant_type": "authorization_code",
    }

    # 요청 보내기
    response = requests.post(url, data=body_data, headers={
                             "Content-Type": "application/x-www-form-urlencoded"})

    # 응답 처리
    if response.status_code != 200:
        raise Exception(f"Error from Apple server: {response.text}")

    res_json = response.json()
    if "error" in res_json:
        raise Exception(f"Apple response error: {res_json}")

    return res_json


if __name__ == "__main__":
    apple_user_token = "ca801461cdff348e7baea450611d94739.0.rrys.N9aYkkx1ZT8UVK3SowYjUg"
    res = get_apple_token_info(apple_user_token)
    print(res)
