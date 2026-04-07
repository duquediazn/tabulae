from datetime import timedelta
from app.utils.authentication import create_access_token, ACCESS_TOKEN_DURATION
import pytest
from app.tests.utils import create_user_in_db, get_token_for_user


def test_active_user_can_connect_websocket(client, session):
    create_user_in_db(session, "User", "user@example.com", "pass123", is_active=True)
    token = get_token_for_user(client, "user@example.com", "pass123")

    with client.websocket_connect("/ws/stock-moves") as ws:
        ws.send_text(token)
        # If the connection is successful and the token is valid, we should be able to receive messages (or at least not get an error).

def test_user_cannot_connect_websocket_with_invalid_token(client, session):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/stock-moves") as ws:
            ws.send_text("este.token.es.falso")
            ws.receive_text()
            # We expect an exception because the token is invalid, so the connection should be closed by the server.

def test_inactive_user_cannot_connect_websocket(client, session):
    user = create_user_in_db(
        session, "Inactive", "inactive@example.com", "pass123", is_active=False
    )
    token = create_access_token(
        {"sub": str(user.id)},  
        expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION),
    )

    with pytest.raises(Exception):
        with client.websocket_connect("/ws/stock-moves") as ws:
            ws.send_text(token)
            ws.receive_text()
            # We expect an exception because the user is inactive, so the connection should be closed by the server.