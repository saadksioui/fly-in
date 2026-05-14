from typing import Any, Dict, List
from src.data import Connection, Graph, Drone, Zone
import heapq

class Simulation:
    def __init__(self, graph: Graph, drones: List[Drone], nbr_drones: int, loc_drones: Dict[str, List[Drone]]) -> None:
        self.graph = graph
        self.drones = drones
        self.loc_drones = loc_drones
        self.turns = 0
        self.drones_delivered = 0
        self.total_drones = nbr_drones
        self.logs = []
        self.type_zone = {
                "normal": 1.0,
                "restricted": 2.0,
                "priority": 0.9,
                "blocked": float("inf")
                }

    @staticmethod
    def _print_path(path):
        for p in path:
            print(f"name: {p.name}")
    
    def _get_path(self, previous: Dict[str, Any]):
        end = self.graph.end_hub
        path = []
        while end is not None:
            path.append(end)
            end = previous[end.name]
        path.reverse()
        return path

    def find_path(self, start: Zone, penalties: Dict[str, float]):
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
                    new_distance = self.type_zone[z.zone_b.metadata.zone_type] + distance + penalties[v.name]
                    if new_distance < distances[v.name]:
                        distances[v.name] = new_distance
                        previous[v.name] = zone_object
                        heapq.heappush(hq, (distances[v.name], v.name, v))
        return self._get_path(previous) 

    def calculate_routes(self, start: Zone):
        penalties = {zone.name: 0.0 for zone in self.graph.elements.keys()}
        for i, drone in enumerate(self.drones):
            path = self.find_path(start, penalties)
            drone.path = path
            for pa in path:
                if pa.name == "start" or pa.name == "goal":
                    continue
                penalties[pa.name] += (2.0 / pa.metadata.max_drones)
            if i % 3 == 0:
                for zone_name in penalties:
                    penalties[zone_name] = max(0.0, penalties[zone_name] - 0.5)
                      
    def run_simulation(self):
        half_move = []
        while self.drones_delivered < self.total_drones:
            self.turns += 1
            logs = []
            for drone, connection, next_zone in half_move:
                index = self.loc_drones[connection.name].index(drone)
                self.loc_drones[connection.name].pop(index)
                drone.current_location = next_zone
                self.loc_drones[next_zone.name].append(drone)
                drone.path.pop(1)
                logs.append(f"{drone.id}-{next_zone.name}")
                if next_zone.prefix == "end_hub":
                    self.drones_delivered += 1
                    drone.done = 1
            half_move.clear()
            can_move = []
            for drone in self.drones:
                if drone.done:
                    continue
                next_des = drone.path[1]
                old_des = drone.current_location
                d_index = self.loc_drones[old_des.name].index(drone)
                self.loc_drones[old_des.name].pop(d_index)
                can_move.append((old_des, drone, next_des))
            
            for old, drone, next in can_move:
                if (len(self.loc_drones[next.name]) == next.metadata.max_drones
                    and next.prefix != "end_hub"):
                    self.loc_drones[old.name].append(drone)
                else:
                    if next.metadata.zone_type == "restricted":
                        connection: Connection | None = None
                        for zone, conn in self.graph.elements.get(old, []):
                            if zone == next:
                                connection = conn
                                break
                        self.loc_drones[connection.name].append(drone)
                        drone.current_location = connection
                        half_move.append((drone, connection, next))
                        logs.append(f"{drone.id}-{connection.name}")
                    else:
                        drone.current_location = next
                        self.loc_drones[next.name].append(drone)
                        drone.path.pop(1)
                        logs.append(f"{drone.id}-{next.name}")
                        if next.prefix == "end_hub":
                            drone.done = 1
                            self.drones_delivered += 1
            self.logs.append(" ".join(logs))
            print(" ".join(logs))
        print(f"Total turns: {self.turns}")
