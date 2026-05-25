import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "mysql+aiomysql://root:123456@localhost:3306/quantmind?charset=utf8mb4")

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.qq.com")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True"
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-change-me")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_DAYS", "1")))
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30")))

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
