from google.oauth2 import service_account
from googleapiclient.discovery import build

# 서비스 계정 키 파일 경로
KEY_FILE = 'careease-iap.json'

# Google Play Developer API에 접근하기 위한 스코프
SCOPES = ['https://www.googleapis.com/auth/androidpublisher']

# 서비스 계정 인증
credentials = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=SCOPES)

# Google Play Developer API 서비스 구축
service = build('androidpublisher', 'v3', credentials=credentials)

# 앱의 구매 정보를 가져오기 위한 API 호출 (예: 인앱 구매 정보)
package_name = 'io.lokks.careease'
product_id = 'android.tier.1'
purchase_token = 'mnpgedbhjfggjlbbbdmeeknd.AO-J1OxGxMf0tSq-Pel28o8lMZFYwZjU5b8LlzvE-M1Ub-kl_WnTG5vmer3V98WFM_qSDhG9lYCvuqg2uhY8Way5mOH1HUZeYw'

try:
    response = service.purchases().products().get(
        packageName=package_name,
        productId=product_id,
        token=purchase_token).execute()
except Exception as e:
    print(e)
    response = None

# response = service.purchases().products().get(
#     packageName=package_name,
#     productId=product_id,
#     token=purchase_token).execute()

print(response)
