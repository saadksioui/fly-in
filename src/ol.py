import pygame
import random
from typing import List, Dict
from src.data import Graph

# --- Colors ---
COLORS = {
    "background": (30, 30, 30),
    "text": (255, 255, 255),
    "line": (100, 100, 100),
    "drone": (0, 255, 255),  # Cyan drones
    "normal": (200, 200, 200),
    "restricted": (255, 100, 100),
    "priority": (255, 215, 0),
    "blocked": (50, 50, 50),
    "start_hub": (0, 255, 0),
    "end_hub": (255, 0, 255)
}

class Visualizer:
    def __init__(self, graph: Graph, logs: List[str], total_drones: int):
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in Drone Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        self.large_font = pygame.font.SysFont("Arial", 24, bold=True)

        self.graph = graph
        self.logs = logs
        self.total_turns = len(logs)
        self.current_turn = 0
        
        # Animation state
        self.animating = False
        self.progress = 0.0
        self.anim_speed = 0.05  # 0.05 = 20 frames per turn
        self.auto_play = False

        # Calculate map scaling
        self._calculate_scale()

        # Drone State Tracking
        # All drones start at the start_hub
        start_name = self.graph.start_hub.name
        self.drone_positions = {f"D{i}": start_name for i in range(1, total_drones + 1)}
        self.drone_targets = self.drone_positions.copy()
        
        # Give each drone a tiny random offset so they don't perfectly overlap
        self.drone_offsets = {f"D{i}": (random.randint(-8, 8), random.randint(-8, 8)) for i in range(1, total_drones + 1)}

    def _calculate_scale(self):
        """Finds the min/max coordinates to center and scale the graph on screen."""
        xs = [z.x for z in self.graph.elements.keys()]
        ys = [z.y for z in self.graph.elements.keys()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        grid_width = max(1, max_x - min_x)
        grid_height = max(1, max_y - min_y)
        
        padding = 100
        scale_x = (self.width - padding * 2) / grid_width
        scale_y = (self.height - padding * 2) / grid_height
        
        self.scale = min(scale_x, scale_y)
        self.offset_x = padding - (min_x * self.scale)
        self.offset_y = padding - (min_y * self.scale)

    def _get_coords(self, location_name: str) -> pygame.math.Vector2:
        """Returns the screen (X, Y) for a zone or the midpoint of a connection."""
        # Is it a zone?
        for zone in self.graph.elements.keys():
            if zone.name == location_name:
                x = zone.x * self.scale + self.offset_x
                y = zone.y * self.scale + self.offset_y
                return pygame.math.Vector2(x, y)
        
        # Is it a connection? (For restricted zones)
        for zone, connections in self.graph.elements.items():
            for neighbor, conn in connections:
                if conn.name == location_name:
                    x1 = conn.zone_a.x * self.scale + self.offset_x
                    y1 = conn.zone_a.y * self.scale + self.offset_y
                    x2 = conn.zone_b.x * self.scale + self.offset_x
                    y2 = conn.zone_b.y * self.scale + self.offset_y
                    # Return the exact midpoint of the line
                    return pygame.math.Vector2((x1 + x2) / 2, (y1 + y2) / 2)
        
        return pygame.math.Vector2(0, 0) # Fallback

    def _advance_turn(self):
        """Reads the next line of the log and sets up the targets for animation."""
        if self.current_turn >= self.total_turns:
            self.auto_play = False
            return

        # Current targets become the new starting positions
        self.drone_positions = self.drone_targets.copy()
        
        # Parse the log line: "D1-roof1 D2-connection-5"
        log_line = self.logs[self.current_turn]
        if log_line.strip():
            moves = log_line.split(" ")
            for move in moves:
                drone_id, destination = move.split("-", 1)
                self.drone_targets[drone_id] = destination

        self.current_turn += 1
        self.progress = 0.0
        self.animating = True

    def draw(self):
        self.screen.fill(COLORS["background"])

        # 1. Draw Connections (Lines)
        drawn_lines = set()
        for zone, connections in self.graph.elements.items():
            for neighbor, conn in connections:
                if conn.name not in drawn_lines:
                    start = self._get_coords(conn.zone_a.name)
                    end = self._get_coords(conn.zone_b.name)
                    pygame.draw.line(self.screen, COLORS["line"], start, end, 3)
                    drawn_lines.add(conn.name)

        # 2. Draw Zones (Circles)
        for zone in self.graph.elements.keys():
            pos = self._get_coords(zone.name)
            
            # Determine color
            color = COLORS["normal"]
            if zone.prefix == "start_hub": color = COLORS["start_hub"]
            elif zone.prefix == "end_hub": color = COLORS["end_hub"]
            elif zone.metadata.zone_type in COLORS: color = COLORS[zone.metadata.zone_type]

            pygame.draw.circle(self.screen, color, (int(pos.x), int(pos.y)), 20)
            pygame.draw.circle(self.screen, (0,0,0), (int(pos.x), int(pos.y)), 20, 2) # Border

            # Draw Zone Name
            text = self.font.render(zone.name, True, COLORS["text"])
            self.screen.blit(text, (pos.x - text.get_width()//2, pos.y - 35))

        # 3. Draw Drones
        for drone_id in self.drone_positions.keys():
            start_pos = self._get_coords(self.drone_positions[drone_id])
            target_pos = self._get_coords(self.drone_targets[drone_id])
            
            # Lerp for smooth animation
            current_pos = start_pos.lerp(target_pos, self.progress)
            
            # Add jitter so drones don't perfectly overlap
            offset_x, offset_y = self.drone_offsets[drone_id]
            draw_x = int(current_pos.x + offset_x)
            draw_y = int(current_pos.y + offset_y)

            pygame.draw.circle(self.screen, COLORS["drone"], (draw_x, draw_y), 6)
            pygame.draw.circle(self.screen, (0,0,0), (draw_x, draw_y), 6, 1)

        # 4. Draw UI
        ui_text = self.large_font.render(f"Turn: {self.current_turn} / {self.total_turns}", True, COLORS["text"])
        self.screen.blit(ui_text, (20, 20))
        
        controls = self.font.render("SPACE: Next Turn | ENTER: Auto-Play | ESC: Quit", True, COLORS["text"])
        self.screen.blit(controls, (20, 50))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            # Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and not self.animating:
                        self._advance_turn()
                    elif event.key == pygame.K_RETURN:
                        self.auto_play = not self.auto_play

            # Handle Animation Logic
            if self.animating:
                self.progress += self.anim_speed
                if self.progress >= 1.0:
                    self.progress = 1.0
                    self.animating = False
            elif self.auto_play:
                self._advance_turn()

            self.draw()
            self.clock.tick(60) # 60 FPS

        pygame.quit()
