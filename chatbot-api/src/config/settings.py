import os
from dotenv import load_dotenv

# 환경 설정 로드
load_dotenv()

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# JWT 설정
JWT_SECRET = os.getenv("JWT_SECRET")

# MySQL 설정
MYSQL_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE")
} 