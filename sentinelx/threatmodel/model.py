from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List

class Threat(Enum):
    SPOOFING = "S"
    TAMPERING = "T"
    REPUDIATION = "R"
    INFORMATION_DISCLOSURE = "I"
    DENIAL_OF_SERVICE = "D"
    ELEVATION_OF_PRIVILEGE = "E"

@dataclass
class Asset:
    name: str
    threats: List[Threat] = field(default_factory=list)

@dataclass
class ThreatModel:
    assets: List[Asset] = field(default_factory=list)
