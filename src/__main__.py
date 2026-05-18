from typing import Dict, List, Any
from src.custom_exception import (
    ConnectionException,
    HubException,
    ParsingException
)
from src.parser import Parser
from src.data import Zone, Metadata, Connection, Graph, Drone
from src.simulation import Simulation
from src.visual import Visualization
import sys


class Engine:
    def __init__(self):
        self.start_hub = None
        self.end_hub = None
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.drones: List[Drone] = []
        self.loc_drones: Dict[str, List[Drone]] = {}

    def run(self):
        if len(sys.argv) != 2:
            print("This how to run the program: python3 -m src <map path>")
            exit(1)
        try:
            pars = Parser(sys.argv[1])
            parsed_data: Dict[str, Any] = pars.parser()
            for zone in parsed_data["hubs"]:
                if zone["prefix"] == "start_hub":
                    start_metadata = Metadata(zone["metadata"]["zone"],
                                              zone["metadata"]["color"],
                                              zone["metadata"]["max_drones"])
                    start_hub = Zone(zone["prefix"], zone["name"], zone["x"],
                                     zone["y"], start_metadata)
                    self.zones[zone["name"]] = start_hub
                    self.loc_drones[start_hub.name] = []
                elif zone["prefix"] == "end_hub":
                    end_metadata = Metadata(zone["metadata"]["zone"],
                                            zone["metadata"]["color"],
                                            zone["metadata"]["max_drones"])
                    end_hub = Zone(zone["prefix"], zone["name"], zone["x"],
                                   zone["y"], end_metadata)
                    self.zones[zone["name"]] = end_hub
                    self.loc_drones[end_hub.name] = []
                else:
                    metadata_obj = Metadata(zone["metadata"]["zone"],
                                            zone["metadata"]["color"],
                                            zone["metadata"]["max_drones"])
                    zone_obj = Zone(zone["prefix"], zone["name"], zone["x"],
                                    zone["y"], metadata_obj)
                    self.zones[zone["name"]] = zone_obj
                    self.loc_drones[zone_obj.name] = []

            if start_hub is None:
                print("Error: Start zone not found")
                exit(1)

            for connection in parsed_data["connections"]:
                name = connection["name"]
                zone_a = self.zones[connection["from"]]
                zone_b = self.zones[connection["to"]]
                capacity = int(connection["metadata"]["max_link_capacity"])
                conn = Connection(name=name, zone_a=zone_a, zone_b=zone_b,
                                  metadata=capacity)
                self.connections.append(conn)
                self.loc_drones[conn.name] = []
            for i in range(1, parsed_data["nb_drones"] + 1):
                drone = Drone(f"D{i}", start_hub)
                self.drones.append(drone)
                self.loc_drones[start_hub.name].append(drone)

            graph = Graph(start_hub, end_hub)

            for con in self.connections:
                graph.add_connection(con)
            sim = Simulation(graph, self.drones,
                             parsed_data["nb_drones"], self.loc_drones)
            sim.calculate_routes(start_hub)
            sim.run_simulation()
            vi = Visualization(parsed_data, sim.logs)
            vi.run()

        except FileNotFoundError as e:
            print(e)
            exit(1)
        except PermissionError as e:
            print(e)
            exit(1)
        except (ParsingException, HubException, ConnectionException) as e:
            print(e)
            exit(1)
        except ValueError as e:
            print(e)
            exit(1)


if __name__ == "__main__":
    engine = Engine()
    engine.run()
