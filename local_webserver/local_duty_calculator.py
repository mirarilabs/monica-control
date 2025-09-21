"""
Local Duty Calculator for Real-time Key Control

This module provides local duty calculation for real-time key control,
eliminating network latency by calculating optimal finger positions and
cart movements locally on the computer instead of sending commands to the Pico.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from monica_pathing import Wagon, Chord, Duty
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import wagon, keyboard
import time

@dataclass
class ActiveKey:
    """Represents an active key press"""
    finger: int
    position: int  # 0=Left, 1=Right
    timestamp: float

@dataclass
class KeyControlState:
    """Current state of key control system"""
    active_keys: Dict[str, ActiveKey]  # key -> ActiveKey
    current_cart_position: int
    current_volume_percent: int
    last_update_time: float

class LocalDutyCalculator:
    """Calculates optimal duty for real-time key control locally"""
    
    def __init__(self):
        # Initialize wagon with Monica's configuration
        # Use the local Wagon class from monica_pathing.py
        self.wagon = Wagon(valid_positions=wagon["valid_positions"])
        
        # Key mapping from HTML
        self.key_mapping = {
            'a': [0, 0], 's': [0, 1], 'd': [1, 0], 'f': [1, 1],
            'g': [2, 0], 'h': [2, 1], 'j': [3, 0], 'k': [3, 1],
            'w': [4, 0], 'e': [4, 1], 'r': [5, 0], 't': [5, 1],
            'y': [6, 0], 'u': [6, 1], 'i': [6, 1]
        }
        
        # Initialize state
        self.state = KeyControlState(
            active_keys={},
            current_cart_position=0,
            current_volume_percent=50,
            last_update_time=time.time()
        )
        
        # Finger states (True = at home, False = pressed)
        self.finger_states = [True] * 7  # 7 fingers
        
    def key_down(self, key: str) -> Dict:
        """Handle key press - calculate optimal duty locally"""
        if key not in self.key_mapping:
            return {"error": f"Invalid key: {key}"}
            
        finger, position = self.key_mapping[key]
        
        # Add to active keys
        self.state.active_keys[key] = ActiveKey(
            finger=finger,
            position=position,
            timestamp=time.time()
        )
        
        # Update finger state
        self.finger_states[finger] = False
        
        # Calculate optimal duty for current chord
        duty_result = self._calculate_optimal_duty()
        
        return {
            "success": True,
            "key": key,
            "finger": finger,
            "position": position,
            "duty": duty_result,
            "active_keys_count": len(self.state.active_keys)
        }
    
    def key_up(self, key: str) -> Dict:
        """Handle key release - recalculate duty"""
        if key not in self.key_mapping:
            return {"error": f"Invalid key: {key}"}
            
        finger, position = self.key_mapping[key]
        
        # Remove from active keys
        if key in self.state.active_keys:
            del self.state.active_keys[key]
        
        # Update finger state
        # Check if any other keys are using this finger
        finger_in_use = any(
            active_key.finger == finger 
            for active_key in self.state.active_keys.values()
        )
        self.finger_states[finger] = not finger_in_use
        
        # Recalculate optimal duty for remaining keys
        duty_result = self._calculate_optimal_duty()
        
        return {
            "success": True,
            "key": key,
            "finger": finger,
            "position": position,
            "duty": duty_result,
            "active_keys_count": len(self.state.active_keys)
        }
    
    def _calculate_optimal_duty(self) -> Dict:
        """Calculate optimal duty based on currently active keys"""
        if not self.state.active_keys:
            return {
                "type": "silence",
                "cart_position": self.state.current_cart_position,
                "fingerings": [None] * 7,
                "volume_percent": self.state.current_volume_percent
            }
        
        # Convert active keys to chord
        chord = self._active_keys_to_chord()
        if not chord:
            return {
                "type": "silence",
                "cart_position": self.state.current_cart_position,
                "fingerings": [None] * 7,
                "volume_percent": self.state.current_volume_percent
            }
        
        # Find optimal cart position for this chord
        optimal_position = self._find_optimal_position(chord)
        
        # Calculate fingerings for optimal position
        fingerings = self.wagon.calculate_fingerings(chord, optimal_position)
        
        # Determine if cart movement is needed
        cart_movement = None
        if optimal_position != self.state.current_cart_position:
            cart_movement = {
                "from": self.state.current_cart_position,
                "to": optimal_position,
                "steps": self.wagon.calculate_steps(optimal_position)
            }
            self.state.current_cart_position = optimal_position
        
        return {
            "type": "chord",
            "chord": str(chord),
            "cart_position": optimal_position,
            "fingerings": fingerings,
            "volume_percent": self.state.current_volume_percent,
            "cart_movement": cart_movement,
            "active_fingers": self._get_active_fingers()
        }
    
    def _active_keys_to_chord(self) -> Optional[Chord]:
        """Convert currently active keys to a Chord object"""
        if not self.state.active_keys:
            return None
            
        # For now, create a simple chord representation
        # This is a simplified version - in a full implementation, 
        # we would need to map keys to actual notes based on cart position
        notes = []
        for i, active_key in enumerate(self.state.active_keys.values()):
            # Create a simple note representation
            # In reality, this would depend on the actual keyboard layout
            note_name = f"Note_{active_key.finger}_{active_key.position}"
            notes.append(note_name)
        
        if not notes:
            return None
            
        return Chord(notes)
    
    def _find_optimal_position(self, chord: Chord) -> int:
        """Find optimal cart position for the given chord"""
        # Get covering qualities for all positions
        qualities = self.wagon.covering_qualities(chord)
        
        # Find position with highest quality
        if not qualities:
            return self.state.current_cart_position
            
        optimal_position = max(range(len(qualities)), key=lambda i: qualities[i])
        
        # If multiple positions have the same quality, prefer staying in current position
        # to minimize unnecessary movement
        if (qualities[optimal_position] == qualities[self.state.current_cart_position] and
            self.state.current_cart_position < len(qualities)):
            return self.state.current_cart_position
            
        return optimal_position
    
    def _get_active_fingers(self) -> List[Dict]:
        """Get information about currently active fingers"""
        active_fingers = []
        for i, state in enumerate(self.finger_states):
            if not state:  # Not at home (active)
                # Find which key is controlling this finger
                controlling_key = None
                for key, active_key in self.state.active_keys.items():
                    if active_key.finger == i:
                        controlling_key = key
                        break
                
                active_fingers.append({
                    "finger": i,
                    "position": self.state.active_keys[controlling_key].position if controlling_key else None,
                    "key": controlling_key
                })
        
        return active_fingers
    
    def get_status(self) -> Dict:
        """Get current status of the local duty calculator"""
        return {
            "active_keys": len(self.state.active_keys),
            "cart_position": self.state.current_cart_position,
            "volume_percent": self.state.current_volume_percent,
            "finger_states": self.finger_states.copy(),
            "active_fingers": self._get_active_fingers(),
            "last_update": self.state.last_update_time
        }
    
    def set_cart_position(self, position: int) -> Dict:
        """Update cart position (for external cart movement)"""
        if 0 <= position < self.wagon.valid_positions:
            self.state.current_cart_position = position
            return {"success": True, "position": position}
        return {"error": f"Invalid position: {position}"}
    
    def set_volume(self, volume_percent: int) -> Dict:
        """Update volume percentage"""
        if 0 <= volume_percent <= 100:
            self.state.current_volume_percent = volume_percent
            return {"success": True, "volume_percent": volume_percent}
        return {"error": f"Invalid volume: {volume_percent}"}
    
    def home_all(self) -> Dict:
        """Reset all fingers to home position"""
        self.state.active_keys.clear()
        self.finger_states = [True] * 7
        
        return {
            "success": True,
            "message": "All fingers homed",
            "finger_states": self.finger_states.copy()
        }

# Global instance for the web server to use
local_duty_calculator = LocalDutyCalculator()
