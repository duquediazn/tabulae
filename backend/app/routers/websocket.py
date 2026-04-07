
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.utils.authentication import decode_access_token
from app.models.database import get_db
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlmodel import Session, select
from app.models.user import User

router = APIRouter()


class ConnectionManager:
    """This class stores all active WebSocket connections in a list.
    Each time a client connects, the connection is added to the list."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()  # Establish the connection with the client.
    
    def authorize(self, websocket: WebSocket):
        self.active_connections.append(websocket)  
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)  

    async def broadcast(self, message: str):
        """This method sends a text message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_text(message)


# Instantiate so it can be used anywhere in the code
manager = ConnectionManager()


@router.websocket("/ws/stock-moves")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    # Accept the connection first to allow receiving messages (like the token) from the client.
    await manager.connect(websocket) 
   
    try:
        # Expect the client to send the token immediately after connecting
        token = await websocket.receive_text() 
        payload = decode_access_token(token)  # This will raise an exception if the token is invalid or expired
    except Exception:
        await websocket.close(code=1008)  # 1008 = Policy Violation
        return
    
    # If we got here, the token is valid. Now we check if the user exists and is active.
    user_id = int(payload.get("sub"))
    user = db.exec(select(User).where(User.id == user_id)).first()

    if not user or not user.is_active:
        await websocket.close(code=1008) 
        return

    manager.authorize(websocket)  # Add to active connections after successful authentication.

    try:
        # Keep the connection alive with an infinite loop.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
