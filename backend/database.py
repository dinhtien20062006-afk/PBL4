import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        # Cấu hình thông tin máy chủ MySQL của bạn
        self.host = 'localhost'
        self.database = 'pbl4_mail_nids'
        self.user = 'root'
        self.password = ''
        self.connection = None

    def connect(self):
        """Hàm thiết lập kết nối đến MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Đã kết nối thành công tới CSDL:", self.database)
                return self.connection
        except Error as e:
            print(f"Lỗi khi kết nối MySQL: {e}")
            return None

    def disconnect(self):
        """Hàm đóng kết nối an toàn"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Đã đóng kết nối CSDL.")


if __name__ == "__main__":
    # Khởi tạo đối tượng Database
    db = Database()
    
    # Thử kết nối
    conn = db.connect()
    
    if conn:
        try:
            # Lấy thông tin phiên bản MySQL để xác nhận
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE(), VERSION();")
            record = cursor.fetchone()
            print(f"Bạn đang dùng Database: {record[0]} - Phiên bản MySQL: {record[1]}")
            
            # Đóng con trỏ
            cursor.close()
        except Error as e:
            print("Lỗi truy vấn:", e)
        finally:
            # Luôn nhớ ngắt kết nối sau khi dùng xong
            db.disconnect()