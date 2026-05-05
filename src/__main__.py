from src.parser import Parser

if __name__ == "__main__":
    pars = Parser('easy')
    data = pars.parser()
    nbr_drones = data[0]['nbr_drones']
    hubs = data[0]['hubs']
    connections = data[0]['connections']
    print(nbr_drones)
    print(hubs)
    print(connections)