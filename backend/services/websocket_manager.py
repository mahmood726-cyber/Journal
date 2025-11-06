"""
WebSocket Manager for Real-Time Updates.
Provides instant notifications without page refresh.
"""
from typing import Dict, Set, List
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Types of real-time notifications."""
    MANUSCRIPT_STATUS = "manuscript_status"
    NEW_REVIEW = "new_review"
    REVIEW_COMPLETED = "review_completed"
    EDITOR_DECISION = "editor_decision"
    NEW_MESSAGE = "new_message"
    DEADLINE_REMINDER = "deadline_reminder"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"


class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates.

    Features:
    - User-specific connections
    - Broadcast to groups
    - Online presence
    - Message queuing for offline users
    """

    def __init__(self):
        # Active connections: user_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}

        # User groups: group_name -> Set[user_id]
        self.groups: Dict[str, Set[int]] = {}

        # Message queue for offline users: user_id -> List[message]
        self.offline_queue: Dict[int, List[Dict]] = {}

        # Online users
        self.online_users: Set[int] = set()

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Connect user's WebSocket.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()

        # Add connection
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

        # Mark user as online
        was_offline = user_id not in self.online_users
        self.online_users.add(user_id)

        # Send queued messages if user was offline
        if was_offline and user_id in self.offline_queue:
            for message in self.offline_queue[user_id]:
                await self.send_personal_message(message, user_id)
            del self.offline_queue[user_id]

        # Broadcast user online status
        await self.broadcast_user_status(user_id, online=True)

        print(f"User {user_id} connected. Active connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Disconnect user's WebSocket.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # If no more connections, mark user as offline
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                self.online_users.discard(user_id)

                # Broadcast user offline status
                await self.broadcast_user_status(user_id, online=False)

        print(f"User {user_id} disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict, user_id: int):
        """
        Send message to specific user.

        Args:
            message: Message dict
            user_id: Target user ID
        """
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.utcnow().isoformat()

        # If user is online, send immediately
        if user_id in self.active_connections:
            message_json = json.dumps(message)
            # Send to all user's connections (multiple devices)
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    print(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)

            # Remove failed connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
        else:
            # Queue message for offline user
            if user_id not in self.offline_queue:
                self.offline_queue[user_id] = []
            self.offline_queue[user_id].append(message)

            # Limit queue size (keep last 100 messages)
            self.offline_queue[user_id] = self.offline_queue[user_id][-100:]

    async def broadcast(self, message: Dict):
        """
        Broadcast message to all connected users.

        Args:
            message: Message dict
        """
        message['timestamp'] = datetime.utcnow().isoformat()
        message_json = json.dumps(message)

        for user_id in list(self.active_connections.keys()):
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message_json)
                except:
                    pass

    async def broadcast_to_group(self, message: Dict, group_name: str):
        """
        Broadcast message to a group of users.

        Args:
            message: Message dict
            group_name: Group name (e.g., "editors", "reviewers")
        """
        if group_name in self.groups:
            message['timestamp'] = datetime.utcnow().isoformat()
            for user_id in self.groups[group_name]:
                await self.send_personal_message(message, user_id)

    def add_to_group(self, user_id: int, group_name: str):
        """Add user to a group."""
        if group_name not in self.groups:
            self.groups[group_name] = set()
        self.groups[group_name].add(user_id)

    def remove_from_group(self, user_id: int, group_name: str):
        """Remove user from a group."""
        if group_name in self.groups:
            self.groups[group_name].discard(user_id)

    async def broadcast_user_status(self, user_id: int, online: bool):
        """
        Broadcast user online/offline status.

        Args:
            user_id: User ID
            online: True if online, False if offline
        """
        message = {
            'type': NotificationType.USER_ONLINE if online else NotificationType.USER_OFFLINE,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Broadcast to all users (for presence indicators)
        await self.broadcast(message)

    def get_online_users(self) -> List[int]:
        """Get list of currently online user IDs."""
        return list(self.online_users)

    def is_user_online(self, user_id: int) -> bool:
        """Check if user is currently online."""
        return user_id in self.online_users

    async def notify_manuscript_status(
        self,
        user_id: int,
        manuscript_id: int,
        old_status: str,
        new_status: str
    ):
        """
        Notify user of manuscript status change.

        Args:
            user_id: User to notify
            manuscript_id: Manuscript ID
            old_status: Previous status
            new_status: New status
        """
        message = {
            'type': NotificationType.MANUSCRIPT_STATUS,
            'manuscript_id': manuscript_id,
            'old_status': old_status,
            'new_status': new_status,
            'message': f'Manuscript status changed from {old_status} to {new_status}',
        }
        await self.send_personal_message(message, user_id)

    async def notify_new_review(
        self,
        user_id: int,
        manuscript_id: int,
        reviewer_name: str
    ):
        """
        Notify editor/author of new review received.

        Args:
            user_id: User to notify
            manuscript_id: Manuscript ID
            reviewer_name: Reviewer's name
        """
        message = {
            'type': NotificationType.NEW_REVIEW,
            'manuscript_id': manuscript_id,
            'reviewer_name': reviewer_name,
            'message': f'New review received from {reviewer_name}',
        }
        await self.send_personal_message(message, user_id)

    async def notify_editor_decision(
        self,
        user_id: int,
        manuscript_id: int,
        decision: str,
        editor_name: str
    ):
        """
        Notify author of editor decision.

        Args:
            user_id: Author to notify
            manuscript_id: Manuscript ID
            decision: Editorial decision
            editor_name: Editor's name
        """
        message = {
            'type': NotificationType.EDITOR_DECISION,
            'manuscript_id': manuscript_id,
            'decision': decision,
            'editor_name': editor_name,
            'message': f'Editorial decision: {decision}',
        }
        await self.send_personal_message(message, user_id)

    async def notify_deadline_reminder(
        self,
        user_id: int,
        task_type: str,
        task_id: int,
        due_date: str,
        days_remaining: int
    ):
        """
        Notify user of approaching deadline.

        Args:
            user_id: User to notify
            task_type: Type of task (review, revision, etc.)
            task_id: Task ID
            due_date: Due date string
            days_remaining: Days until deadline
        """
        message = {
            'type': NotificationType.DEADLINE_REMINDER,
            'task_type': task_type,
            'task_id': task_id,
            'due_date': due_date,
            'days_remaining': days_remaining,
            'message': f'{task_type.capitalize()} due in {days_remaining} days',
            'priority': 'high' if days_remaining <= 2 else 'medium'
        }
        await self.send_personal_message(message, user_id)


# Singleton instance
ws_manager = WebSocketManager()
