"""
SentinelX Red Team Operations Module

This module provides comprehensive red team capabilities including:
- Command and Control (C2) operations
- Lateral movement techniques  
- Social engineering campaigns and simulations

For authorized penetration testing and security assessment only.
"""

from .c2 import C2Operations
from .lateral_move import LateralMovement
from .social_eng import SocialEngineering

__all__ = [
    "C2Operations",
    "LateralMovement", 
    "SocialEngineering"
]
