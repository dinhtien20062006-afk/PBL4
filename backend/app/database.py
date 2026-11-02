from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import mysql.connector

# Cấu hình chuỗi kết nối SQLAlchemy (dùng driver mysqlconnector)
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/pbl4_mail_nids"

# Khởi tạo Engine (tương tự như Pool, SQLAlchemy tự quản lý Connection Pool)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,        # Giữ sẵn 10 kết nối cùng lúc (giống code cũ)
    max_overflow=20,     # Số kết nối tối đa có thể vượt quá pool_size khi quá tải
    pool_pre_ping=True   # Kiểm tra kết nối trước khi dùng để tránh lỗi đứt kết nối
)

# Tạo class Session để tương tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các Models kế thừa
Base = declarative_base()

# Dependency để lấy database session cho các FastAPI Router
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Trả kết nối về lại Pool

# Giữ lại hàm check_db_status để API Health Check trong main.py vẫn hoạt động
class Database:
    def check_db_status(self):
        try:
            # Thử tạo một kết nối ngắn để kiểm tra
            with engine.connect() as conn:
                return True
        except Exception as e:
            print(f"Lỗi kiểm tra trạng thái CSDL: {e}")
            return False