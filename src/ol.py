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
        self.drones_in_transit = []
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
                    new_distance = self.type_zone[v.metadata.zone_type] + distance + penalties[v.name]
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
                      
    def _get_connection_between(self, zone_a: Zone, zone_b: Zone):
        """Return the connection object linking two adjacent zones."""
        for neighbor, connection in self.graph.elements[zone_a]:
            if neighbor.name == zone_b.name:
                return connection
        return None

    def run_simulation(self):
        while self.drones_delivered < self.total_drones:
            moves = []
            self.turns += 1

            # Finish restricted-zone moves that started on the previous turn.
            # These drones moved to the connection last turn; only now do they
            # enter the restricted zone.
            arrived_this_turn = set()
            still_in_transit = []
            for drone, zone, connection in self.drones_in_transit:
                if connection.name in self.loc_drones and drone in self.loc_drones[connection.name]:
                    self.loc_drones[connection.name].remove(drone)

                if len(self.loc_drones[zone.name]) < zone.metadata.max_drones:
                    self.loc_drones[zone.name].append(drone)
                    drone.current_location = zone
                    arrived_this_turn.add(drone.id)
                    moves.append(f"{drone.id}-{zone.name}")

                    if zone.prefix == "end_hub":
                        self.drones_delivered += 1
                        drone.done = 1
                else:
                    # This should not happen because restricted arrivals are
                    # capacity-checked before entering transit, but keep the
                    # drone in transit instead of overfilling the zone.
                    still_in_transit.append((drone, zone, connection))

            self.drones_in_transit = still_in_transit

            # Loop 1: departures. Remove every moving drone from its current
            # location before checking destination capacity. This makes movement
            # simultaneous: a drone leaving a full zone frees space for another
            # drone during the same turn.
            planned_moves = []
            for drone in self.drones:
                if drone.done or drone.id in arrived_this_turn:
                    continue
                if len(drone.path) < 2:
                    continue

                cur_loc = drone.current_location
                next_des = drone.path[1]
                connection = self._get_connection_between(cur_loc, next_des)
                if connection is None:
                    continue

                planned_moves.append((drone, cur_loc, next_des, connection))
                if drone in self.loc_drones[cur_loc.name]:
                    self.loc_drones[cur_loc.name].remove(drone)

            # Loop 2: arrivals. Now that all departures have happened, check
            # whether each destination has space. Failed moves are restored to
            # their old locations and keep the same path step for a later turn.
            restricted_reservations = {}
            for _, zone, _ in self.drones_in_transit:
                restricted_reservations[zone.name] = restricted_reservations.get(zone.name, 0) + 1

            for drone, old_zone, zone, connection in planned_moves:
                reserved = restricted_reservations.get(zone.name, 0)
                destination_full = (
                    len(self.loc_drones[zone.name]) + reserved >= zone.metadata.max_drones
                )

                if destination_full:
                    self.loc_drones[old_zone.name].append(drone)
                    continue

                drone.path.pop(1)

                if zone.metadata.zone_type == "restricted":
                    self.drones_in_transit.append((drone, zone, connection))
                    restricted_reservations[zone.name] = reserved + 1
                    if connection.name in self.loc_drones:
                        self.loc_drones[connection.name].append(drone)
                    moves.append(f"{drone.id}-{connection.name}")
                else:
                    self.loc_drones[zone.name].append(drone)
                    drone.current_location = zone
                    moves.append(f"{drone.id}-{zone.name}")

                    if zone.prefix == "end_hub":
                        self.drones_delivered += 1
                        drone.done = 1

            print(" ".join(moves))

        print(f"The number of turns is: {self.turns}")
