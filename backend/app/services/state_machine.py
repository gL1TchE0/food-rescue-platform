"""
M7 Logistics - CRITICAL: Volunteer State Machine
Implements the strict FSM flow control with server-side guards
Version: 1.0.0

STATE FLOW:
OFFLINE → ONLINE → ASSIGNED → NAVIGATING_TO_DONOR → PICKUP_VERIFIED 
→ IN_TRANSIT → DROPOFF_VERIFIED → COMPLETED → ONLINE

Exception State: Can trigger from any active state
"""
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VolunteerState(str, Enum):
    """Volunteer state enumeration"""
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ASSIGNED = "ASSIGNED"
    NAVIGATING_TO_DONOR = "NAVIGATING_TO_DONOR"
    PICKUP_VERIFIED = "PICKUP_VERIFIED"
    IN_TRANSIT = "IN_TRANSIT"
    DROPOFF_VERIFIED = "DROPOFF_VERIFIED"
    COMPLETED = "COMPLETED"
    EXCEPTION = "EXCEPTION"


class TaskState(str, Enum):
    """Task state enumeration"""
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXCEPTION = "EXCEPTION"


class TransitionError(Exception):
    """Raised when an invalid state transition is attempted"""
    pass


class StateMachine:
    """
    Enforces state transitions with guards
    Single source of truth for workflow control
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        VolunteerState.OFFLINE: [VolunteerState.ONLINE],
        VolunteerState.ONLINE: [VolunteerState.ASSIGNED, VolunteerState.OFFLINE],
        VolunteerState.ASSIGNED: [
            VolunteerState.NAVIGATING_TO_DONOR,
            VolunteerState.ONLINE,  # Cancel before navigation
            VolunteerState.EXCEPTION
        ],
        VolunteerState.NAVIGATING_TO_DONOR: [
            VolunteerState.PICKUP_VERIFIED,
            VolunteerState.EXCEPTION
        ],
        VolunteerState.PICKUP_VERIFIED: [
            VolunteerState.IN_TRANSIT,
            VolunteerState.EXCEPTION
        ],
        VolunteerState.IN_TRANSIT: [
            VolunteerState.DROPOFF_VERIFIED,
            VolunteerState.EXCEPTION
        ],
        VolunteerState.DROPOFF_VERIFIED: [VolunteerState.COMPLETED],
        VolunteerState.COMPLETED: [VolunteerState.ONLINE],
        VolunteerState.EXCEPTION: [
            VolunteerState.ONLINE,  # After resolution
            VolunteerState.OFFLINE
        ]
    }
    
    # Task state mapping to volunteer state
    TASK_STATE_MAPPING = {
        VolunteerState.ASSIGNED: TaskState.ASSIGNED,
        VolunteerState.NAVIGATING_TO_DONOR: TaskState.IN_PROGRESS,
        VolunteerState.PICKUP_VERIFIED: TaskState.PICKED_UP,
        VolunteerState.IN_TRANSIT: TaskState.IN_TRANSIT,
        VolunteerState.DROPOFF_VERIFIED: TaskState.DELIVERED,
        VolunteerState.COMPLETED: TaskState.COMPLETED,
        VolunteerState.EXCEPTION: TaskState.EXCEPTION
    }
    
    @classmethod
    def can_transition(cls, from_state: VolunteerState, to_state: VolunteerState) -> bool:
        """
        Check if transition is valid
        
        Args:
            from_state: Current volunteer state
            to_state: Desired volunteer state
            
        Returns:
            bool: True if transition is allowed
        """
        if from_state not in cls.VALID_TRANSITIONS:
            return False
        return to_state in cls.VALID_TRANSITIONS[from_state]
    
    @classmethod
    def transition(
        cls,
        current_state: VolunteerState,
        target_state: VolunteerState,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Attempt state transition with validation
        
        Args:
            current_state: Current volunteer state
            target_state: Target state to transition to
            context: Additional context (task_id, location, etc.)
            
        Returns:
            dict: Transition result with new state and side effects
            
        Raises:
            TransitionError: If transition is invalid
        """
        if not cls.can_transition(current_state, target_state):
            raise TransitionError(
                f"Invalid transition from {current_state} to {target_state}"
            )
        
        # Execute guards based on transition
        cls._execute_guards(current_state, target_state, context or {})
        
        # Determine side effects
        side_effects = cls._get_side_effects(current_state, target_state, context or {})
        
        logger.info(
            f"State transition: {current_state} → {target_state}",
            extra={"context": context}
        )
        
        return {
            "new_state": target_state,
            "task_state": cls.TASK_STATE_MAPPING.get(target_state),
            "side_effects": side_effects,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def _execute_guards(
        cls,
        from_state: VolunteerState,
        to_state: VolunteerState,
        context: Dict[str, Any]
    ):
        """
        Execute guard conditions before transition
        
        Raises:
            TransitionError: If guard fails
        """
        # Guard: PICKUP_VERIFIED requires QR scan
        if to_state == VolunteerState.PICKUP_VERIFIED:
            if not context.get("qr_verified"):
                raise TransitionError("Pickup verification requires QR scan")
        
        # Guard: DROPOFF_VERIFIED requires QR scan
        if to_state == VolunteerState.DROPOFF_VERIFIED:
            if not context.get("qr_verified"):
                raise TransitionError("Dropoff verification requires QR scan")
        
        # Guard: NAVIGATING requires task assignment
        if to_state == VolunteerState.NAVIGATING_TO_DONOR:
            if not context.get("task_id"):
                raise TransitionError("Navigation requires active task assignment")
        
        # Guard: EXCEPTION requires issue type
        if to_state == VolunteerState.EXCEPTION:
            if not context.get("issue_type"):
                raise TransitionError("Exception state requires issue type")
    
    @classmethod
    def _get_side_effects(
        cls,
        from_state: VolunteerState,
        to_state: VolunteerState,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine side effects for transition
        
        Returns:
            dict: Actions to be executed (notifications, tracking, etc.)
        """
        effects = {
            "notify_volunteer": False,
            "notify_donor": False,
            "notify_dispatcher": False,
            "start_tracking": False,
            "stop_tracking": False,
            "calculate_performance": False
        }
        
        # NAVIGATING_TO_DONOR: Start GPS tracking, notify donor
        if to_state == VolunteerState.NAVIGATING_TO_DONOR:
            effects["start_tracking"] = True
            effects["notify_donor"] = True
            effects["notify_volunteer"] = True
        
        # PICKUP_VERIFIED: Notify NGO, update ETA
        if to_state == VolunteerState.PICKUP_VERIFIED:
            effects["notify_ngo"] = True
            effects["notify_volunteer"] = True
        
        # IN_TRANSIT: Continue tracking with perishability checks
        if to_state == VolunteerState.IN_TRANSIT:
            effects["enable_perishability_check"] = True
        
        # DROPOFF_VERIFIED: Stop tracking
        if to_state == VolunteerState.DROPOFF_VERIFIED:
            effects["stop_tracking"] = True
            effects["notify_ngo"] = True
        
        # COMPLETED: Calculate performance stats
        if to_state == VolunteerState.COMPLETED:
            effects["calculate_performance"] = True
            effects["notify_volunteer"] = True
        
        # EXCEPTION: Freeze workflow, alert dispatcher
        if to_state == VolunteerState.EXCEPTION:
            effects["stop_tracking"] = True
            effects["notify_dispatcher"] = True
            effects["freeze_workflow"] = True
        
        return effects
    
    @classmethod
    def get_available_actions(cls, current_state: VolunteerState) -> list:
        """
        Get list of available actions for current state
        Used by mobile app UI
        """
        transitions = cls.VALID_TRANSITIONS.get(current_state, [])
        
        action_map = {
            VolunteerState.ONLINE: ["Go Offline", "Accept Task (when available)"],
            VolunteerState.OFFLINE: ["Go Online"],
            VolunteerState.ASSIGNED: ["Start Navigation", "Cancel Task"],
            VolunteerState.NAVIGATING_TO_DONOR: ["Scan QR at Pickup", "Report Exception"],
            VolunteerState.PICKUP_VERIFIED: ["Start Transit to NGO"],
            VolunteerState.IN_TRANSIT: ["Scan QR at Dropoff", "Report Exception"],
            VolunteerState.DROPOFF_VERIFIED: ["Complete Task"],
            VolunteerState.COMPLETED: ["Return to Online"],
            VolunteerState.EXCEPTION: ["Resolve Issue", "Go Offline"]
        }
        
        return action_map.get(current_state, [])


# Singleton instance
state_machine = StateMachine()
