"""
WebSocket API endpoint for real-time updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from api.auth import get_current_user_ws, get_current_user
from services.websocket_manager import ws_manager
from db.models import User
import json


router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time updates.

    Authenticates user via token in query string.
    Maintains persistent connection for instant notifications.

    Usage:
        ws://localhost:8000/api/v1/ws/123?token=eyJ0eXAiOiJKV1QiLCJhb...
    """
    # Verify user ID matches authenticated user
    if current_user.id != user_id:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    # Connect user
    await ws_manager.connect(websocket, user_id)

    # Add user to appropriate groups based on role
    if current_user.role in ['editor_in_chief', 'associate_editor']:
        ws_manager.add_to_group(user_id, 'editors')
    if current_user.role == 'reviewer':
        ws_manager.add_to_group(user_id, 'reviewers')

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()

            # Handle ping/pong for keep-alive
            if data == "ping":
                await websocket.send_text("pong")
            else:
                # Handle other client messages if needed
                try:
                    message = json.loads(data)
                    # Process client messages (e.g., mark notification as read)
                    if message.get('action') == 'mark_read':
                        # Handle mark as read
                        pass
                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, user_id)


@router.get("/online-users")
async def get_online_users(current_user: User = Depends(get_current_user)):
    """
    Get list of currently online users.

    Only available to editors and administrators.
    """
    if current_user.role not in ['admin', 'editor_in_chief', 'associate_editor']:
        return {'error': 'Unauthorized'}

    online_users = ws_manager.get_online_users()
    return {
        'online_users': online_users,
        'count': len(online_users)
    }


@router.post("/broadcast")
async def broadcast_message(
    message: str,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast system announcement to all users.

    Only available to administrators.
    """
    if current_user.role != 'admin':
        return {'error': 'Unauthorized'}

    await ws_manager.broadcast({
        'type': 'system_announcement',
        'message': message,
        'sender': current_user.full_name
    })

    return {'status': 'broadcast_sent'}
