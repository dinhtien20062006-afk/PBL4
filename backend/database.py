import mysql.connector
from mysql.connector import Error, pooling

class Database:
    _pool = None # Biến tĩnh (class variable) để giữ Pool duy nhất

    def __init__(self):
        self.host = 'localhost'
        self.database = 'pbl4_mail_nids'
        self.user = 'root'
        self.password = ''
        
        # Chỉ khởi tạo Pool nếu nó chưa tồn tại (Singleton)
        if Database._pool is None:
            try:
                Database._pool = pooling.MySQLConnectionPool(
                    pool_name="nids_pool",
                    pool_size=10, # Giữ sẵn 10 kết nối cùng lúc
                    pool_reset_session=True,
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                print("Khởi tạo Connection Pool thành công.")
            except Error as e:
                print(f"Lỗi khởi tạo Connection Pool: {e}")

    def get_connection(self):
        """Lấy một kết nối từ Pool"""
        try:
            if Database._pool:
                return Database._pool.get_connection()
            return None
        except Error as e:
            print(f"Lỗi lấy kết nối: {e}")
            return None

    def check_db_status(self):
        """Kiểm tra và cập nhật trạng thái hoạt động của DB"""
        conn = self.get_connection()
        if conn and conn.is_connected():
            conn.close() # Trả lại pool
            return True
        return False