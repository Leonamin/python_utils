import requests

CAREPLANNER_ADMIN_TEST_URL = "https://admin-careplanner-test.careease.kr/v1"
LOGIN_URL = CAREPLANNER_ADMIN_TEST_URL + "/account/signin"
# {email: "test@caresquare.kr", password: "admin1234567890"}
LOGIN_DATA = {"email": "test@caresquakr.kr", "password": "admin1234567890"}

# 로그인
response = requests.post(LOGIN_URL, data=LOGIN_DATA)
print(response.status_code)
print(response.text)