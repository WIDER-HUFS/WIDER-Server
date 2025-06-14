import os
from dotenv import load_dotenv

# 환경 설정 로드
load_dotenv()

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# JWT 설정
JWT_SECRET_KEY = "yourSecretKeyShouldBeLongAndSecureAndStoredInEnvironmentVariables"  # 실제 운영 환경에서는 환경 변수로 관리해야 합니다
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MySQL 설정
MYSQL_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE")
} 

print(MYSQL_CONFIG)