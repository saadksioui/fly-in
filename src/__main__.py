from os import name
from src.parser import Parser
from src.data import Zone, Metadata, Connection, Graph, Drone
from src.simulation import Simulation
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("This how to run the program: python3 -m src <map path>")
        exit(1)
    pars = Parser(sys.argv[1])
    data = pars.parser()
    parsed_data = data[0]
    drones = []
    zones = {}
    connections = []
    start_hub = None
    end_hub = None
    loc_drones = {}
    for zone in parsed_data["hubs"]:
        if zone["prefix"] == "start_hub":
            start_metadata = Metadata(zone["metadata"]["zone"], zone["metadata"]["color"], zone["metadata"]["max_drones"])
            start_hub = Zone(zone["prefix"], zone["name"], zone["x"], zone["y"], start_metadata)
            zones[zone["name"]] = start_hub
            loc_drones[start_hub.name] = []
        elif zone["prefix"] == "end_hub":
            end_metadata = Metadata(zone["metadata"]["zone"], zone["metadata"]["color"], zone["metadata"]["max_drones"])
            end_hub = Zone(zone["prefix"], zone["name"], zone["x"], zone["y"], end_metadata)
            zones[zone["name"]] = end_hub
            loc_drones[end_hub.name] = []
        else:
            metadata_obj = Metadata(zone["metadata"]["zone"], zone["metadata"]["color"], zone["metadata"]["max_drones"]) 
            zone_obj = Zone(zone["prefix"], zone["name"], zone["x"], zone["y"], metadata_obj)
            zones[zone["name"]] = zone_obj
            loc_drones[zone_obj.name] = []
    
    if start_hub is None:
        print("Error: Start zone not found")
        exit(1)

    for connection in parsed_data["connections"]:
        name = connection["name"]
        zone_a = zones[connection["con_from"]]
        zone_b = zones[connection["con_to"]]
        capacity = connection["metadata"]["max_link_capacity"]
        conn = Connection(name=name, zone_a=zone_a, zone_b=zone_b, metadata=capacity)        
        connections.append(conn)
        loc_drones[conn.name] = []
    for i in range(1, parsed_data["nbr_drones"] + 1):
        drone = Drone(f"D{i}", start_hub)
        drones.append(drone)
        loc_drones[start_hub.name].append(drone)

    graph = Graph(start_hub, end_hub)
    
    for con in connections:
        graph.add_connection(con)
    sim = Simulation(graph, drones, parsed_data["nbr_drones"], loc_drones)
    sim.calculate_routes(start_hub)
    sim.run_simulation()

