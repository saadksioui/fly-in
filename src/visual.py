from typing import Any, Dict, List
import pygame


class Visualization:
    def __init__(self, data: Dict[str, Any], logs: List[str]) -> None:
        self.data = data
        self.logs = logs
        self.width = 1920
        self.height = 1080

        self.hubs = {}
        self.connections = {}
        self.drones = {}
        self.turns = 0

        self.x_zones = []
        self.y_zones = []
        self.scale = 0
        self.off_x = 0
        self.off_y = 0

    def _setup(self):
        self.hubs = {h["name"]: h for h in self.data["hubs"]}
        self.connections = {c["name"]: c for c in self.data["connections"]}
        self.drones = {f"D{i}": self.data['hubs'][0]['name']
                       for i in range(1, self.data['nb_drones'] + 1)}
        self.x_zones = [h["x"] for h in self.hubs.values()]
        self.y_zones = [h["y"] for h in self.hubs.values()]
        self.scale = min(self.width /
                         max(1, max(self.x_zones) - min(self.x_zones)),
                         self.height /
                         max(1, max(self.y_zones) - min(self.y_zones))) * 0.7
        self.off_x = 100 - min(self.x_zones) * self.scale
        self.off_y = 100 - min(self.y_zones) * self.scale

    def _get_pos(self, name):
        if name in self.hubs.keys():
            if self.hubs[name]['x'] >= self.width:
                raise ValueError(f"Line {self.hubs[name]['line_no']}: "
                                 "The x value is not in screen")
            if self.hubs[name]['y'] >= self.height:
                raise ValueError(f"Line {self.hubs[name]['line_no']}: "
                                 "The y value is not in screen")

            return (int(self.hubs[name]['x'] * self.scale + self.off_x),
                    int(self.hubs[name]['y'] * self.scale + self.off_y))
        conn = self.connections[name]
        x = (self.hubs[conn['from']]['x'] + self.hubs[conn['to']]['x']) / 2
        y = (self.hubs[conn['from']]['y'] + self.hubs[conn['to']]['y']) / 2
        return (int(x * self.scale + self.off_x),
                int(y * self.scale + self.off_y))

    def _get_color(self, color_name):
        if color_name is None or color_name.lower() == "none":
            return (200, 200, 200)
        try:
            return pygame.Color(color_name)
        except ValueError:
            return (200, 200, 200)

    def run(self):
        self._setup()
        running = True
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height),
                                         pygame.RESIZABLE)
        font = pygame.font.SysFont("Arial", 10, bold=True)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_SPACE
                        and self.turns < len(self.logs)):
                    for move in self.logs[self.turns].split():
                        drone_id, location = move.split('-', 1)
                        self.drones[drone_id] = location
                    self.turns += 1
            screen.fill((30, 30, 30))
            for c in self.connections.values():
                pygame.draw.line(screen, (100, 100, 100),
                                 self._get_pos(c['from']),
                                 self._get_pos(c['to']), 4)

            for h in self.hubs.values():
                pos = self._get_pos(h['name'])
                color = self._get_color(h['metadata']['color'])
                pygame.draw.circle(screen, color, pos, 25)
                screen.blit(font.render(h['name'], True,
                                        (255, 255, 255)), (pos[0] - 30,
                                                           pos[1] - 50))

            for d_id, loc in self.drones.items():
                pos = self._get_pos(loc)
                pygame.draw.circle(screen, (0, 255, 255), pos, 12)
                screen.blit(font.render(d_id, True, (0, 0, 0)),
                            (pos[0] - 10, pos[1] - 10))

            screen.blit(font.render(f"Turn: {self.turns} / {len(self.logs)} "
                                    "(Press SPACE)", True, (255, 255,
                                                            255)), (20, 20))

            pygame.display.flip()
