import re
from typing import List, Dict, Any
from src.custom_exception import (
    HubException,
    ConnectionException,
    ParsingException
)


class Parser:
    def __init__(self, path: str):
        self.path = path
        self.pattern = r'\[.*?\]|\S+'
        self.hub_names = []
        self.data: List[Dict[str, Any]] = []

    def get_hubs(self, line: str):
        parts = re.findall(self.pattern, line)
        metadata = {"zone": "normal", "color": None, "max_drones": 1}
        if len(parts) != 4 and len(parts) != 5:
            raise HubException(
                "Zone declarations should be like this: "
                "prefix: <name> <x> <y> [metadata]`"
            )

        prefix = parts[0].replace(':', '')
        if prefix not in ['start_hub', 'hub', 'end_hub']:
            raise HubException("The prefix should only be: 'start_hub', "
                               "'hub' or 'end_hub'")

        name = parts[1]
        if '-' in name:
            raise HubException('Dashes are forbiden in zone names')
        self.hub_names.append(name)
        x = int(parts[2])
        y = int(parts[3])

        if len(parts) == 5:
            metadata_part = parts[4]
            if (not metadata_part.startswith('[')
                    and not metadata_part.endswith(']')):
                raise HubException('The metadata should be in []')
            metadata_part = metadata_part.replace('[', '')
            metadata_part = metadata_part.replace(']', '')
            for data in metadata_part.split(' '):
                if '=' not in data:
                    continue
                key, value = data.split('=', 1)
    
                if key not in ['zone', 'color', 'max_drones']:
                    raise HubException(f"Invalid metadata key: {key}")
        
                if key == 'max_drones':
                    metadata['max_drones'] = int(value)
                else:
                    metadata[key] = value

        hub = {
            "prefix": prefix,
            "name": name,
            "x": x,
            "y": y,
            "metadata": metadata
        }
        return hub

    def get_connections(self, line: str):
        parts = re.findall(self.pattern, line)
        if len(parts) not in [2, 3]:
            raise ConnectionException(
                "Connection declarations should be like this: "
                "'connection: name1-name2'"
            )
        metadata = {
            'max_link_capacity': 1
        }
        con_from = parts[1].split('-')[0]
        con_to = parts[1].split('-')[1]
        if con_from not in self.hub_names:
            raise ConnectionException('')
        if con_to not in self.hub_names:
            raise ConnectionException('')

        if len(parts) == 3:
            metadata_part = parts[2]
            if (not metadata_part.startswith('[')
                    and not metadata_part.endswith(']')):
                raise HubException('The metadata should be in []')
            metadata_part = metadata_part.replace('[', '')
            metadata_part = metadata_part.replace(']', '')
            for data in metadata_part.split(' '):
                data_parts = data.split('=')
                if data_parts[0] != "max_link_capacity":
                    raise HubException("The args in metadata should only be: "
                                       "'max_link_capacity'")
                metadata.update({data_parts[0]: data_parts[1]})
        connection = {
            'con_from': con_from,
            'con_to': con_to,
            'metadata': metadata
        }
        return connection

    def get_data(self, data: str):
        lines = data.split("\n")
        hubs = []
        connections = []
        found_nbr = False
        info = {"nbr_drones": 0, "hubs": [], "connections": []}
        for line in lines:
            if line.startswith("nb_drones:") and not found_nbr:
                info['nbr_drones'] = int(line.split(" ")[1])
                found_nbr = True
            elif (
                line.startswith("hub:")
                or line.startswith("start_hub")
                or line.startswith("end_hub")
            ):
                hubs.append(line)
            elif line.startswith("connection:"):
                connections.append(line)

        if len(hubs) <= 2:
            raise ParsingException('')
        if len(connections) == 0:
            raise ParsingException('')
        for hub in hubs:
            info['hubs'].append(self.get_hubs(hub))
        for conn in connections:
            info['connections'].append(self.get_connections(conn))
        return info

    def parser(self):
        with open(self.path) as f:
            data = f.read()
        self.data.append(self.get_data(data))
        return self.data
