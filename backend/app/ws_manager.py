from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass # Bỏ qua nếu client đã ngắt kết nối đột ngột

manager = ConnectionManager()


# ----TEST THU LOI WEBSOCKET---
# from fastapi import WebSocket

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#         print(f"[WebSocket] 🟢 Client kết nối thành công! Đang có {len(self.active_connections)} kết nối.")

#     def disconnect(self, websocket: WebSocket):
#         if websocket in self.active_connections:
#             self.active_connections.remove(websocket)
#         print(f"[WebSocket] 🔴 Client ngắt kết nối. Còn lại {len(self.active_connections)} kết nối.")

#     async def broadcast(self, message: dict):
#         print(f"[WebSocket] 🚀 Chuẩn bị đẩy báo động cho {len(self.active_connections)} client...")
#         for connection in self.active_connections:
#             try:
#                 await connection.send_json(message)
#                 print("[WebSocket] ✅ Đã đẩy JSON thành công xuống Client!")
#             except Exception as e:
#                 print(f"[WebSocket] ❌ LỖI GỬI DỮ LIỆU: {e}")

# manager = ConnectionManager()