import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    MONGO_URI = os.getenv("MONGO_URI")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

settings = Settings()
