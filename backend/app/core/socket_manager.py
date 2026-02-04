"""
M7 Logistics - WebSocket Manager (Socket.IO)
Real-time location streaming and event broadcasting
"""
import socketio
from typing import Dict, Set, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SocketManager:
    """
    Manages WebSocket connections and real-time events
    Handles volunteer location streaming and dispatcher notifications
    """
    
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins='*',
            logger=False,
            engineio_logger=False
        )
        
        # Track connected clients
        self.volunteer_sessions: Dict[str, str] = {}  # {volunteer_id: session_id}
        self.dispatcher_sessions: Set[str] = set()     # {session_ids}
        self.donor_sessions: Dict[str, str] = {}       # {task_id: session_id}
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register Socket.IO event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Client connected"""
            logger.info(f"Client connected: {sid}")
            return True
        
        @self.sio.event
        async def disconnect(sid):
            """Client disconnected - cleanup"""
            logger.info(f"Client disconnected: {sid}")
            
            # Remove from tracking
            for vol_id, session_id in list(self.volunteer_sessions.items()):
                if session_id == sid:
                    del self.volunteer_sessions[vol_id]
            
            self.dispatcher_sessions.discard(sid)
            
            for task_id, session_id in list(self.donor_sessions.items()):
                if session_id == sid:
                    del self.donor_sessions[task_id]
        
        @self.sio.on('volunteer_register')
        async def handle_volunteer_register(sid, data):
            """
            Volunteer registers their session
            Payload: {"volunteer_id": "uuid"}
            """
            volunteer_id = data.get('volunteer_id')
            if volunteer_id:
                self.volunteer_sessions[volunteer_id] = sid
                await self.sio.emit('registered', {'status': 'success'}, room=sid)
                logger.info(f"Volunteer {volunteer_id} registered with session {sid}")
        
        @self.sio.on('dispatcher_register')
        async def handle_dispatcher_register(sid, data):
            """Dispatcher joins monitoring room"""
            self.dispatcher_sessions.add(sid)
            await self.sio.emit('registered', {'status': 'success', 'role': 'dispatcher'}, room=sid)
            logger.info(f"Dispatcher registered: {sid}")
        
        @self.sio.on('donor_track_task')
        async def handle_donor_track(sid, data):
            """
            Donor subscribes to task tracking
            Payload: {"task_id": "uuid"}
            """
            task_id = data.get('task_id')
            if task_id:
                self.donor_sessions[task_id] = sid
                await self.sio.emit('tracking_started', {'task_id': task_id}, room=sid)
                logger.info(f"Donor tracking task {task_id}")
        
        @self.sio.on('location_update')
        async def handle_location_update(sid, data):
            """
            Volunteer sends location update
            Payload: {
                "volunteer_id": "uuid",
                "task_id": "uuid",
                "lat": 12.xxx,
                "lng": 77.xxx,
                "speed": 45,
                "heading": 90
            }
            """
            try:
                volunteer_id = data.get('volunteer_id')
                task_id = data.get('task_id')
                
                # Broadcast to dispatcher
                await self._broadcast_to_dispatchers({
                    'event': 'volunteer_location',
                    'volunteer_id': volunteer_id,
                    'task_id': task_id,
                    'location': {
                        'lat': data.get('lat'),
                        'lng': data.get('lng'),
                        'speed': data.get('speed', 0),
                        'heading': data.get('heading', 0)
                    },
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Broadcast to donor if tracking this task
                if task_id in self.donor_sessions:
                    donor_sid = self.donor_sessions[task_id]
                    await self.sio.emit('volunteer_location_update', data, room=donor_sid)
                
            except Exception as e:
                logger.error(f"Error processing location update: {e}")
    
    async def send_task_assignment(self, volunteer_id: str, task_data: dict):
        """
        Push task assignment to volunteer
        Triggers modal on mobile app
        """
        if volunteer_id in self.volunteer_sessions:
            sid = self.volunteer_sessions[volunteer_id]
            await self.sio.emit('task_assigned', task_data, room=sid)
            logger.info(f"Task assignment sent to volunteer {volunteer_id}")
    
    async def notify_state_change(self, volunteer_id: str, new_state: str, task_id: Optional[str] = None):
        """Notify volunteer of state transition"""
        if volunteer_id in self.volunteer_sessions:
            sid = self.volunteer_sessions[volunteer_id]
            await self.sio.emit('state_changed', {
                'new_state': new_state,
                'task_id': task_id
            }, room=sid)
    
    async def broadcast_exception(self, task_id: str, exception_data: dict):
        """Alert dispatcher of task exception"""
        await self._broadcast_to_dispatchers({
            'event': 'task_exception',
            'task_id': task_id,
            'data': exception_data
        })
    
    async def _broadcast_to_dispatchers(self, data: dict):
        """Send event to all connected dispatchers"""
        for sid in self.dispatcher_sessions:
            await self.sio.emit('dispatcher_event', data, room=sid)
    
    async def notify_donor(self, task_id: str, event_type: str, data: dict):
        """Send notification to donor tracking this task"""
        if task_id in self.donor_sessions:
            sid = self.donor_sessions[task_id]
            await self.sio.emit(event_type, data, room=sid)
    
    def get_asgi_app(self):
        """Get ASGI application for FastAPI mount"""
        return socketio.ASGIApp(self.sio)


# Global instance
socket_manager = SocketManager()
