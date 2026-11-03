import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

# Đọc cấu hình từ backend/.env (nếu có) -> không phải sửa code khi đổi mật khẩu MySQL
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "pbl4_mail_nids")

# URL.create tự escape ký tự đặc biệt trong mật khẩu (@, :, / ...)
SQLALCHEMY_DATABASE_URL = URL.create(
    "mysql+mysqlconnector",
    username=DB_USER,
    password=DB_PASSWORD or None,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={"charset": "utf8mb4"},
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Database:
    """Giữ lại cho API Health Check ở main.py."""

    def check_db_status(self):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Lỗi kiểm tra trạng thái CSDL: {e}")
            return False
