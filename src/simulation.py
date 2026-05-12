from typing import Any, Dict, List
from src.data import Graph, Drone, Zone
import heapq

class Simulation:
    def __init__(self, graph: Graph, drones: List[Drone], nbr_drones: int) -> None:
        self.graph = graph
        self.drones = drones
        self.turns = 0
        self.drones_delivered = 0
        self.penalty = 0
        self.total_drones = nbr_drones
        self.turn_logs = []
        self.type_zone = {
                "normal": 1.0,
                "restricted": 2.0,
                "priority": 0.9,
                "blocked": float("inf")
                }

    def _get_path(self, previous: Dict[str, Any]):
        end = self.graph.end_hub
        path = []
        while end is not None:
            path.append(end)
            end = previous[end.name]
        path.reverse()
        return path

    def find_path(self, start: Zone):
        distances = {v.name: float('inf') for v in self.graph.elements.keys()}
        previous = {v.name: None for v in self.graph.elements.keys()}
        visited = {v.name: False for v in self.graph.elements.keys()}
        first_zone = start
        distances[first_zone.name] = 0
        hq = []
        heapq.heappush(hq, (distances[first_zone.name], first_zone.name, first_zone))
        while hq:
            distance, name, zone_object = heapq.heappop(hq)
            visited[name] = True
            for v, z in self.graph.elements[zone_object]:
                if not visited[v.name]:
                    new_distance = z + distance + self.penalty
                    if new_distance < distances[v.name]:
                        distances[v.name] = new_distance
                        previous[v.name] = zone_object
                        heapq.heappush(hq, (distances[v.name], v.name, v))
        return self._get_path(previous) 

    def calculate_routes(self, start: Zone):
        for i, drone in enumerate(self.drones):
            self.penalty += 0.01
            path = self.find_path(start)
            drone.path = path
            for pa in path:
                print(f"D{i}: {pa.name}")

    def run_simulation(self):
        pass
