import asyncio

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
        """Gửi song song tới mọi client; client lỗi/đã ngắt sẽ bị loại khỏi danh sách."""
        conns = list(self.active_connections)
        if not conns:
            return
        results = await asyncio.gather(*(c.send_json(message) for c in conns), return_exceptions=True)
        for conn, res in zip(conns, results):
            if isinstance(res, Exception):
                self.disconnect(conn)


manager = ConnectionManager()
