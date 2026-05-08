from src.parser import Parser
from src.data import Zone, PrefixType, ZoneType, Metadata, Connection, Graph, Drone
import sys

def print_object(obj, indent=0, visited=None, name="root"):
    if visited is None:
        visited = set()

    prefix = "    " * indent
    obj_id = id(obj)

    # Prevent infinite recursion on circular references
    if obj_id in visited:
        print(f"{prefix}{name}: <already visited {type(obj).__name__}>")
        return

    # Primitive types
    if isinstance(obj, (str, int, float, bool, type(None))):
        print(f"{prefix}{name}: {obj!r}")
        return

    visited.add(obj_id)

    # Dict
    if isinstance(obj, dict):
        print(f"{prefix}{name}: dict")
        for key, value in obj.items():
            print_object(value, indent + 1, visited, name=f"[{key!r}]")
        return

    # List / Tuple / Set
    if isinstance(obj, (list, tuple, set)):
        print(f"{prefix}{name}: {type(obj).__name__}")
        for i, item in enumerate(obj):
            print_object(item, indent + 1, visited, name=f"[{i}]")
        return

    # Normal object: print attributes
    print(f"{prefix}{name}: {type(obj).__name__}")
    if hasattr(obj, "__dict__"):
        for attr, value in vars(obj).items():
            print_object(value, indent + 1, visited, name=attr)
    else:
        print(f"{prefix}    <no __dict__>")

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
    for zone in parsed_data["hubs"]:
        prefix = zone["prefix"]
        zone_meta = ZoneType(zone["metadata"]["zone"])
        meta_obj = Metadata(
            zone=zone_meta,
            color=zone["metadata"]["color"],
            max_drones=zone["metadata"]["max_drones"]
        )
        hub = Zone(
            prefix=prefix, 
            name=zone["name"], 
            x=zone["x"], 
            y=zone["y"], 
            metadata=meta_obj
        )
        zones[hub.name] = hub
        if prefix == PrefixType.StartHub.value:
            start_hub = hub
        elif prefix == PrefixType.EndHub.value:
            end_hub = hub

    for connection in parsed_data["connections"]:
        zone_a = zones[connection["con_from"]]
        zone_b = zones[connection["con_to"]]
        capacity = connection["metadata"]["max_link_capacity"]
        conn = Connection(zone_a=zone_a, zone_b=zone_b, max_link_capacity=capacity)
        zone_a.connections[zone_b.name] = conn
        zone_b.connections[zone_a.name] = conn
        
        connections.append(conn)


    if start_hub is None:
        print("Error: No start_hub found in map!")
        exit(1)

    for i in range(1, parsed_data["nbr_drones"] + 1):
        drone = Drone(id=f"D{i}", current_location=start_hub)
        drones.append(drone)
        
        start_hub.current_drones.append(drone)

    graph = Graph(
        zones=zones,
        connections=connections,
        drones=drones,
        start_hub=start_hub,
        end_hub=end_hub
    )

    print_object(graph)
