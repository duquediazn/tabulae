from datetime import timedelta
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.utils.authentication import create_access_token, ACCESS_TOKEN_DURATION
from app.routers.websocket import ConnectionManager, websocket_endpoint
from app.main import app
import pytest
from app.tests.utils import create_user_in_db


@pytest.mark.asyncio
async def test_active_user_can_connect_websocket(session):
    user = await create_user_in_db(
        session, "User", "user@example.com", "pass123", is_active=True
    )
    token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION),
    )

    with TestClient(app) as ws_client:
        with ws_client.websocket_connect("/ws/stock-moves") as ws:
            ws.send_text(token)
            # If the connection is successful and token is valid, the socket remains open.


@pytest.mark.asyncio
async def test_user_cannot_connect_websocket_with_invalid_token():
    with pytest.raises(Exception):
        with TestClient(app) as ws_client:
            with ws_client.websocket_connect("/ws/stock-moves") as ws:
                ws.send_text("este.token.es.falso")
                ws.receive_text()
                # We expect an exception because the token is invalid.


@pytest.mark.asyncio
async def test_inactive_user_cannot_connect_websocket(session):
    user = await create_user_in_db(
        session, "Inactive", "inactive@example.com", "pass123", is_active=False
    )
    token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION),
    )

    with pytest.raises(Exception):
        with TestClient(app) as ws_client:
            with ws_client.websocket_connect("/ws/stock-moves") as ws:
                ws.send_text(token)
                ws.receive_text()

@pytest.mark.asyncio
async def test_broadcast_removes_dead_connections_and_delivers_to_live_ones():
    manager = ConnectionManager()

    good_ws = AsyncMock()
    dead_ws = AsyncMock()
    dead_ws.send_text.side_effect = Exception("Connection lost")

    manager.active_connections = [dead_ws, good_ws]

    await manager.broadcast("hello")

    good_ws.send_text.assert_called_once_with("hello")
    assert good_ws in manager.active_connections
    assert dead_ws not in manager.active_connections


@pytest.mark.asyncio
async def test_disconnect_before_sending_token_does_not_try_to_close_again():
    websocket = AsyncMock()
    websocket.receive_text.side_effect = WebSocketDisconnect(code=1001)

    await websocket_endpoint(websocket)

    websocket.accept.assert_called_once()
    websocket.close.assert_not_called()