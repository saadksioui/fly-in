from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

ZTypes = Literal["normal", "blocked", "restricted", "priority"]
zone_value = {
        "normal": 1.0,
        "blocked": float("inf"),
        "restricted": 2.0,
        "priority": 0.9
        }


@dataclass(frozen=True)
class Metadata:
    zone_type: ZTypes = "normal"
    color: Optional[str] = None
    max_drones: int = 1

@dataclass(frozen=True)
class Zone:
    prefix: str
    name: str
    x: int
    y: int
    metadata: Metadata

@dataclass
class Connection:
    zone_a: Zone
    zone_b: Zone
    metadata: int = 1

@dataclass
class Drone:
    id: str
    current_zone: Zone | None
    path: List[Zone] = field(default_factory=list)
    done: bool = False
    turns: int = 0

@dataclass
class Graph:
    elements: Dict[Zone, List[tuple[Zone, float]]] = field(default_factory=dict)

    def add_zone(self, zone: Zone):
        if zone not in self.elements:
            self.elements[zone] = []

    def add_connection(self, connection: Connection):
        self.add_zone(connection.zone_a)
        self.add_zone(connection.zone_b)
        self.elements[connection.zone_a].append((connection.zone_b, zone_value[connection.zone_b.metadata.zone_type]))
        self.elements[connection.zone_b].append((connection.zone_a, zone_value[connection.zone_a.metadata.zone_type]))

