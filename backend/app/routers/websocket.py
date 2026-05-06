
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.utils.authentication import decode_access_token
from app.models.database import AsyncSessionLocal
from sqlmodel import select
from app.models.user import User

router = APIRouter()


class ConnectionManager:
    """This class stores all active WebSocket connections in a list.
    Each time a client connects, the connection is added to the list."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
    
    async def authorize(self, websocket: WebSocket):
        self.active_connections.append(websocket)  
    
    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """This method sends a text message to all connected clients."""
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.active_connections.remove(conn)


# Instantiate so it can be used anywhere in the code
manager = ConnectionManager()


@router.websocket("/ws/stock-moves")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the connection first to allow receiving messages (like the token) from the client.
    await manager.connect(websocket)

    try:
        token = await websocket.receive_text()
        payload = decode_access_token(token)
    except WebSocketDisconnect:
        return # Client disconnected before sending token  
    except Exception:
        await websocket.close(code=1008)  # 1008 = Policy Violation
        return

    # Authenticate with a short-lived DB session, then release the connection back to the pool.
    user_id = int(payload.get("sub"))
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        is_valid = user is not None and user.is_active

    if not is_valid:
        await websocket.close(code=1008)
        return

    await manager.authorize(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
