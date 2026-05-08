from __future__ import annotations
from dataclasses import dataclass, field
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
    zone: ZoneType = ZoneType.Normal
    color: str = "None"
    max_drones: int = 1


@dataclass
class Connection:
    zone_a: Zone
    zone_b: Zone
    max_link_capacity: int
    drones_in_transit: List[Drone] = field(default_factory=list)


@dataclass
class Drone:
    id: str
    current_location: Zone | Connection
    route: List[Zone] = field(default_factory=list)
    has_moved: bool = False


@dataclass
class Zone:
    prefix: PrefixType
    name: str
    x: int
    y: int
    metadata: Metadata
    current_drones: List[Drone] = field(default_factory=list)
    connections: Dict[str, Connection] = field(default_factory=dict)


@dataclass
class Graph:
    zones: Dict[str, Zone] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)
    drones: List[Drone] = field(default_factory=list)
    start_hub: Zone | None = None
    end_hub: Zone | None = None
