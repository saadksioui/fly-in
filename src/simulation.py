from typing import Any, Dict, List
from src.data import Graph, Drone, Zone
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
        for drone in self.drones:
            path = self.find_path(start, penalties)
            drone.path = path
            for pa in path:
                if pa.name == "start" or pa.name == "goal":
                    continue
                penalties[pa.name] += (2.0 / pa.metadata.max_drones)
                      
    def run_simulation(self):
        rest_move = False
        while self.drones_delivered < self.total_drones:
            moves = []
            self.turns += 1
            can_move = []
            half_move = []
            for drone in self.drones:
                if drone.done:
                    continue
                #self._print_path(drone.path)
                next_des = drone.path[1]
                if len(self.loc_drones[next_des.name]) == next_des.metadata.max_drones:
                    continue
                can_move.append((drone, next_des))
                cur_loc = drone.current_location
                if len(self.loc_drones[cur_loc.name]) > 0:
                    if drone in self.loc_drones[cur_loc.name]:
                        index = self.loc_drones[cur_loc.name].index(drone)
                        self.loc_drones[cur_loc.name].pop(index)
                drone.path.pop(1)
                #self._print_path(drone.path)

            for drone, zone in can_move:
                conn = [con[1].name for con in self.graph.elements[zone]
                        if con[1].zone_b.name == zone.name]
                if zone.metadata.zone_type == "restricted":
                    half_move.append((drone, zone))
                    moves.append(f"{drone.id}-{conn[0]}")
                else:
                    if zone.prefix == "end_hub":
                        self.drones_delivered += 1
                        drone.done = 1
                    self.loc_drones[zone.name].append(drone)
                    drone.current_location = zone
                    moves.append(f"{drone.id}-{zone.name}")
            
            for drone, zone in half_move:
                self.loc_drones[zone.name].append(drone)
                moves.append(f"{drone.id}-{zone.name}")
                self.turns += 1
            rest_move = not rest_move
            print(" ".join(moves))
        print(f"The number of turns is: {self.turns}")
