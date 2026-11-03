from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import mysql.connector

# Cấu hình chuỗi kết nối SQLAlchemy (dùng driver mysqlconnector)
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/pbl4_mail_nids"

# Khởi tạo Engine với các tham số tối ưu chịu tải cao cho NIDS
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=50,          # Tăng từ 10 lên 50 kết nối thường trực
    max_overflow=100,      # Tăng từ 20 lên 100 kết nối mở rộng khi bị spam
    pool_timeout=30,       # Thêm: Chờ tối đa 30 giây để lấy kết nối
    pool_recycle=1800,     # Thêm: Tái tạo kết nối mỗi 30 phút tránh lỗi "gone away"
    pool_pre_ping=True     # Giữ nguyên: Kiểm tra kết nối trước khi dùng
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