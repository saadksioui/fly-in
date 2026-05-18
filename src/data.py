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
    capacity: int = 0


@dataclass
class Connection:
    name: str
    zone_a: Zone
    zone_b: Zone
    metadata: int = 1


@dataclass
class Drone:
    id: str
    current_location: Zone | Connection
    path: List[Zone] = field(default_factory=list)
    done: bool = False
    has_turn: bool = False


@dataclass
class Graph:
    start_hub: Zone | None
    end_hub: Zone | None
    elements: Dict[Zone,
                   List[tuple[Zone, Connection]]] = field(default_factory=dict)

    def add_zone(self, zone: Zone) -> None:
        if zone not in self.elements:
            self.elements[zone] = []

    def add_connection(self, connection: Connection) -> None:
        self.add_zone(connection.zone_a)
        self.add_zone(connection.zone_b)
        self.elements[connection.zone_a].append(
            (connection.zone_b, connection)
            )
        self.elements[connection.zone_b].append(
            (connection.zone_a, connection)
            )
