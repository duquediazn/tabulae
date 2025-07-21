
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()


class ConnectionManager:
    """This class stores all active WebSocket connections in a list.
    Each time a client connects, the connection is added to the list."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()  # .accept() is required to establish the connection with the client.
        self.active_connections.append(websocket)  # Add to active connections list.

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)  # Remove from list when client disconnects.

    async def broadcast(self, message: str):
        """This method sends a text message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_text(message)


# Instantiate so it can be used anywhere in the code
manager = ConnectionManager()


@router.websocket("/ws/stock-moves")
async def websocket_endpoint(websocket: WebSocket):
    # Call manager.connect() to accept and store the connection.
    await manager.connect(websocket)

    try:
        # Keep the connection alive with an infinite loop.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # When client disconnects, remove from active connections.
        manager.disconnect(websocket)
