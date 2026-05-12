from src.data import Graph
import heapq

class Simulation:
    def __init__(self, graph: Graph, nbr_drones: int) -> None:
        self.graph = graph
        self.turns = 0
        self.drones_delivered = 0
        self.total_drones = nbr_drones
        self.turn_logs = []
        self.type_zone = {
                "normal": 1.0,
                "restricted": 2.0,
                "priority": 0.9
                }

    def find_path(self):
        distances = {v.name: float('inf') for v in self.graph.elements.keys()}
        previous = {v.name: None for v in self.graph.elements.keys()}
        visited = {v.name: False for v in self.graph.elements.keys()}
        first_zone = list(self.graph.elements.keys())[0]
        distances[first_zone.name] = 0
        hq = []
        heapq.heappush(hq, (distances[first_zone.name], first_zone))
        while hq:
            weight, vertex = heapq.heappop(hq)
            visited[vertex.name] = True
            for v, z in self.graph.elements[vertex]:
                if not visited[v.name]:
                    new_distance = z + weight
                    if new_distance < distances[v.name]:
                        distances[v.name] = new_distance
                        previous[v.name] = vertex.name
                        heapq.heappush(hq, (distances[v.name], v))
        print(distances, previous) 

    def calculate_routes(self):
        pass
    
    def run_simulation(self):
        pass
