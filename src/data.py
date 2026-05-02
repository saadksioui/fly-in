from dataclasses import dataclass
from enum import Enum


class ZoneType(Enum):
    Normal = "normal"
    Blocked = "blocked"
    Restricted = "restricted"
    Priority = "priority"


class PrefixType(Enum):
    StartHub = "start_hub"
    EndHub = "end_hub"
    Hub = "hub"


@dataclass
class Metadata:
    zone: ZoneType = ZoneType.Normal
    color: str = None
    max_drones: int = 1


@dataclass
class Zone:
    prefix: PrefixType
    name: str
    x: int
    y: int
    metadata: Metadata
