from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


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
    zone: ZoneType = ZoneType.Normal.value
    color: str = None
    max_drones: int = 1


@dataclass
class Connection:
    zone_a: Zone
    zone_b: Zone
    max_link_capacity: int


@dataclass
class Drone:
    id: str
    current_location: Zone | Connection
    route: List[Zone]
    has_moved: bool


@dataclass
class Zone:
    prefix: PrefixType
    name: str
    x: int
    y: int
    metadata: Metadata
    current_drones: List[Drone]
    connections: Dict[str, Connection]


@dataclass
class Graph:
    zones: Dict[str, Zone]
    connections: List[Connection]
    drones: List[Drone]
    start_hub: Zone
    end_hub: Zone
