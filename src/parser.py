import re
from typing import Any, Dict, List, Tuple
from src.custom_exception import (
    ConnectionException,
    HubException,
    ParsingException
)


class Parser:
    def __init__(self, path: str) -> None:
        self.path = path
        self.pattern = r'\[.*?\]|\S+'

    def _getlines(self, data: str) -> List[Tuple[int, str]]:
        data_lines = data.split('\n')
        lines = []
        for i, line in enumerate(data_lines):
            line = line.split('#')[0].strip()
            if line == "":
                continue
            lines.append((i+1, line))
        return lines

    def _parse_int(self, value: str, line_no: int, field: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ParsingException(f"Line {line_no}: {field} "
                                   "must be an integer")

    def _get_nbdrones(self, line: str, line_no: int) -> Dict[str, Any]:
        data = {}
        parts = line.split(':', 1)
        if len(parts) != 2:
            raise ParsingException(f"Line {line_no}: The correct syntax for "
                                   "nb_drones is `nb_drones: <number>`")
        if ':' in parts[0] or ':' in parts[1]:
            raise ParsingException(f"Line {line_no}: The correct syntax for "
                                   "nb_drones is `nb_drones: <number>`")
        nbr = self._parse_int(parts[1].strip(), line_no, 'nb_drones')
        if nbr <= 0:
            raise ParsingException(f"Line {line_no}: The nb_drones should be "
                                   "a positive number `>0`")
        data.update({"type": "nb_drones", "line_no": line_no, "value": nbr})
        return data

    def _get_hubs(self, line: str, line_no: int) -> Dict[str, Any]:
        data = {}
        metadata = {"zone": "normal", "color": None, "max_drones": 1}
        prefix, content = line.split(':', 1)
        if ':' in prefix or ':' in content:
            raise HubException(f"Line {line_no}: The correct syntax "
                               "for hubs is "
                               "`<prefix>: <name> <x> <y> <metadata>`")
        parts = re.findall(self.pattern, content)
        if len(parts) != 3 and len(parts) != 4:
            raise HubException(f"Line {line_no}: The correct syntax for hubs "
                               "is `<prefix>: <name> <x> <y> <metadata>`")
        if prefix not in ["start_hub", "end_hub", "hub"]:
            raise HubException("The prefix should only be: 'start_hub', "
                               "'hub' or 'end_hub'")
        name = parts[0]
        x = self._parse_int(parts[1], line_no, 'x')
        y = self._parse_int(parts[2], line_no, 'y')
        if '-' in name:
            raise HubException(f"Line {line_no}: Dashes are forbiden "
                               "in zone names")
        if len(parts) == 4:
            md_part = parts[3]
            if (not md_part.startswith('[')
                    or not md_part.endswith(']')):
                raise HubException(f"Line {line_no}: The metadata "
                                   "should be in []")
            md_part = md_part.replace('[', '')
            md_part = md_part.replace(']', '')
            md_parts = md_part.split(' ')
            found_zone, found_color, found_max = False, False, False
            for part in md_parts:
                if part.strip() == '':
                    continue
                part = part.strip()
                if '=' not in part:
                    raise HubException(f"Line {line_no}: The data inside "
                                       "the metadata should be like "
                                       "this key=value")
                key, value = part.split('=', 1)
                key, value = key.strip(), value.strip()
                if '=' in value:
                    raise HubException(f"Line {line_no}: The data inside "
                                       "the metadata should be like "
                                       "this key=value")
                if key not in ["zone", "color", "max_drones"]:
                    raise HubException(f"Line {line_no}: Invalid metadata "
                                       f"key: {key}")
                if key == "zone":
                    if not found_zone:
                        if (value not in ["normal", "priority",
                                          "restricted", "blocked"]):
                            raise HubException(f"Line {line_no}: The only "
                                               "allowed values for zone is "
                                               "\"normal\", \"priority\", "
                                               "\"restricted\", \"blocked\"")
                        metadata.update({"zone": value})
                        found_zone = True
                    else:
                        raise HubException(f"Line {line_no}: Only one type "
                                           "zone should exist")
                elif key == "color":
                    if not found_color:
                        metadata.update({"color": value})
                        found_color = True
                    else:
                        raise HubException(f"Line {line_no}: Only one color "
                                           "should exist")
                else:
                    if not found_max:
                        max_d = self._parse_int(value, line_no, 'max_drones')
                        if max_d <= 0:
                            raise HubException(f"Line {line_no}: The "
                                               "max_drones should be positive "
                                               "number `>0`")
                        metadata.update({"max_drones": max_d})
                        found_max = True
                    else:
                        raise HubException(f"Line {line_no}: Only one "
                                           "max_drones should exist")
        data.update({"type": "zone", "prefix": prefix, "name": name, "x": x,
                     "y": y, "metadata": metadata, "line_no": line_no})
        return data

    def _get_connection(self, line: str, line_no: int) -> Dict[str, Any]:
        data = {}
        metadata = {"max_link_capacity": 1}
        prefix, content = line.split(':', 1)
        if ':' in prefix or ':' in content:
            raise ConnectionException(f"Line {line_no}: The correct syntax for"
                                      " connection is `connection: "
                                      "<zone_name>-<zone_name> <metadata>`")
        parts = re.findall(self.pattern, content)
        if len(parts) not in [1, 2]:
            raise ConnectionException(f"Line {line_no}: The correct syntax for"
                                      " connection is `connection: "
                                      "<zone_name>-<zone_name> <metadata>`")
        zone_names = parts[0].split('-', 1)
        if len(zone_names) != 2:
            raise ConnectionException(f"Line {line_no}: THe connection should "
                                      "be like this `<zone_name>-<zone_name>`")
        if '-' in zone_names[1]:
            raise ConnectionException(f"Line {line_no}: Dashes are forbiden "
                                      "in zone names")
        if len(parts) == 2:
            md_part = parts[1]
            if (not md_part.startswith('[')
                    or not md_part.endswith(']')):
                raise HubException(f"Line {line_no}: The metadata should "
                                   "be in []")
            md_part = md_part.replace('[', '')
            md_part = md_part.replace(']', '')
            md_part = md_part.strip()
            key, value = md_part.split('=', 1)
            key = key.strip()
            value = value.strip()
            max_c = self._parse_int(value, line_no, 'max_link_capacity')
            if key != "max_link_capacity":
                raise ConnectionException(
                    f"Line {line_no}: The only allowed connection metadata "
                    "key is 'max_link_capacity'"
                )
            if max_c <= 0:
                raise ConnectionException(f"Line {line_no}: The "
                                          "max_link_capacity needs to be "
                                          "positive number `>0`")
            metadata.update({"max_link_capacity": max_c})
        data.update({"type": "connection",
                     "name": f"{zone_names[0]}-{zone_names[1]}",
                     "from": zone_names[0],
                     "to": zone_names[1], "metadata": metadata,
                     "line_no": line_no})

        return data

    def _gettypes(self, lines: List[Tuple[int, str]]) -> List[Dict[str, Any]]:
        found_nbr = False
        found_start = False
        found_end = False
        record = []
        for line_no, line in lines:
            if line.startswith('nb_drones:'):
                if not found_nbr:
                    record.append(self._get_nbdrones(line, line_no))
                    found_nbr = True
                else:
                    raise ParsingException(f"Line {line_no}: Only one "
                                           "nb_drones should exist in "
                                           "the map.")
            elif line.startswith(("start_hub:", "hub:", "end_hub:")):
                if line.startswith("start_hub:"):
                    if not found_start:
                        record.append(self._get_hubs(line, line_no))
                        found_start = True
                    else:
                        raise HubException(f"Line {line_no}: Only one "
                                           "start_hub should exist in "
                                           "the map.")
                elif line.startswith("end_hub:"):
                    if not found_end:
                        record.append(self._get_hubs(line, line_no))
                        found_end = True
                    else:
                        raise HubException(f"Line {line_no}: Only one end_hub "
                                           "should exist in the map.")
                else:
                    record.append(self._get_hubs(line, line_no))
            elif line.startswith('connection:'):
                record.append(self._get_connection(line, line_no))
            else:
                raise ParsingException(f"Line {line_no}: unknown directive")
        if not found_start:
            raise ParsingException("The map must contain "
                                   "exactly one 'start_hub'")
        if not found_end:
            raise ParsingException("The map must contain "
                                   "exactly one 'end_hub'")
        if not found_nbr:
            raise ParsingException("The map must contain 'nb_drones'")
        return record

    def _validate(self,
                  records: List[Dict[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {"nb_drones": 0, "hubs": [],
                                  "connections": []}
        seen_names = set()
        for rec in records:
            if rec["type"] == "nb_drones":
                result["nb_drones"] = rec["value"]
            elif rec["type"] == "zone":
                name = rec["name"]
                if name in seen_names:
                    raise HubException(
                        f"Line {rec['line_no']}: Duplicate zone name '{name}'"
                    )
                seen_names.add(name)
                result["hubs"].append(rec)
            elif rec["type"] == "connection":
                if rec["from"] not in seen_names:
                    raise ConnectionException(
                        f"Line {rec['line_no']}: Unknown "
                        f"zone '{rec['from']}' in connection"
                    )
                if rec["to"] not in seen_names:
                    raise ConnectionException(
                        f"Line {rec['line_no']}: Unknown "
                        f"zone '{rec['to']}' in connection"
                    )
                if rec["from"] == rec["to"]:
                    raise ConnectionException(
                        f"Line {rec['line_no']}: Loop connections "
                        "are not allowed"
                    )

                seen_edges = set()
                edge = tuple(sorted((rec["from"], rec["to"])))
                if edge in seen_edges:
                    raise ConnectionException(
                        f"Line {rec['line_no']}: Duplicate connection "
                        f"'{rec['from']}-{rec['to']}'"
                    )
                seen_edges.add(edge)
                result["connections"].append(rec)

        return result

    def parser(self) -> Dict[str, Any]:
        with open(self.path, 'r') as f:
            data = f.read()
        lines = self._getlines(data)
        if len(lines) == 0:
            raise ParsingException("THe file is empty?")
        if not lines[0][1].startswith("nb_drones"):
            raise ParsingException("The first line must define the number "
                                   "of drones using "
                                   "nb_drones: <positive_integer>.")
        data_types = self._gettypes(lines)
        result = self._validate(data_types)
        return result
