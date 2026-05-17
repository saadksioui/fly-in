import math
from copy import deepcopy
from typing import Dict, List, Tuple

import pygame
from src.data import Graph


COLORS = {
    "background": (14, 18, 28),
    "panel": (28, 34, 48),
    "panel_border": (210, 210, 220),
    "text": (245, 245, 245),
    "muted": (180, 185, 195),
    "line": (130, 140, 160),
    "line_text": (220, 220, 230),
    "drone": (0, 235, 255),
    "drone_text": (10, 18, 22),
    "normal": (190, 195, 210),
    "restricted": (235, 120, 120),
    "priority": (255, 215, 70),
    "blocked": (90, 90, 90),
    "start_hub": (0, 210, 90),
    "end_hub": (215, 95, 255),
    "outline": (10, 10, 10),
    "timeline": (50, 60, 80),
    "timeline_fill": (0, 235, 255),
    "timeline_knob": (255, 255, 255),
}


class Visualizer:
    def __init__(self, graph: Graph, logs: List[str], total_drones: int) -> None:
        pygame.init()

        self.width = 1500
        self.height = 920
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Fly-in Visualizer")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 13)
        self.big_font = pygame.font.SysFont("Arial", 28, bold=True)

        self.graph = graph
        self.logs = logs
        self.total_drones = total_drones

        self.zone_by_name = {z.name: z for z in self.graph.elements.keys()}
        self.connection_by_name = self._collect_connections()

        self.snapshots = self._build_snapshots()
        self.turn_index = 0

        self.auto_play = False
        self.delay_ms = 700
        self.last_tick = 0
        self.running = True

        self.top_ui_h = 135
        self.bottom_ui_h = 55
        self.side_pad = 50
        self.graph_pad = 80

        self.base_zone_radius = 26
        self.min_scale = 35
        self.max_scale = 160

        self.zoom = 1.0
        self.camera_x = 0.0
        self.camera_y = 0.0

        self._recompute_layout()

    # ---------- data prep ----------

    def _collect_connections(self) -> Dict[str, object]:
        out: Dict[str, object] = {}
        for zone, connections in self.graph.elements.items():
            for neighbor, conn in connections:
                out[conn.name] = conn
        return out

    def _build_snapshots(self) -> List[Dict[str, str]]:
        state = {
            f"D{i}": self.graph.start_hub.name
            for i in range(1, self.total_drones + 1)
        }
        snapshots = [deepcopy(state)]

        for raw in self.logs:
            new_state = deepcopy(snapshots[-1])
            moves = raw if isinstance(raw, list) else str(raw).split()
            for move in moves:
                drone_id, destination = move.split("-", 1)
                new_state[drone_id] = destination
            snapshots.append(new_state)

        return snapshots

    # ---------- layout ----------

    def _graph_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.side_pad,
            self.top_ui_h + 10,
            self.width - self.side_pad * 2,
            self.height - self.top_ui_h - self.bottom_ui_h - 25,
        )

    def _recompute_layout(self) -> None:
        xs = [z.x for z in self.graph.elements.keys()]
        ys = [z.y for z in self.graph.elements.keys()]

        self.min_world_x = min(xs)
        self.max_world_x = max(xs)
        self.min_world_y = min(ys)
        self.max_world_y = max(ys)

        world_w = max(1, self.max_world_x - self.min_world_x)
        world_h = max(1, self.max_world_y - self.min_world_y)

        rect = self._graph_rect()
        usable_w = max(200, rect.width - 2 * self.graph_pad)
        usable_h = max(200, rect.height - 2 * self.graph_pad)

        fit_scale = min(usable_w / world_w, usable_h / world_h)
        self.base_scale = max(self.min_scale, min(self.max_scale, fit_scale))

        center_world_x = (self.min_world_x + self.max_world_x) / 2
        center_world_y = (self.min_world_y + self.max_world_y) / 2

        self.center_world_x = center_world_x
        self.center_world_y = center_world_y

        self._clamp_camera()

    def _clamp_camera(self) -> None:
        # keep panning bounded so the map cannot be fully lost
        rect = self._graph_rect()
        pad = 200
        max_dx = rect.width * 0.35 + pad
        max_dy = rect.height * 0.35 + pad
        self.camera_x = max(-max_dx, min(max_dx, self.camera_x))
        self.camera_y = max(-max_dy, min(max_dy, self.camera_y))

    def _current_scale(self) -> float:
        return self.base_scale * self.zoom

    def _world_to_screen(self, x: float, y: float) -> pygame.Vector2:
        rect = self._graph_rect()
        scale = self._current_scale()

        sx = rect.centerx + (x - self.center_world_x) * scale + self.camera_x
        sy = rect.centery + (y - self.center_world_y) * scale + self.camera_y
        return pygame.Vector2(sx, sy)

    def _get_coords(self, location_name: str) -> pygame.Vector2:
        if location_name in self.zone_by_name:
            zone = self.zone_by_name[location_name]
            return self._world_to_screen(zone.x, zone.y)

        if location_name in self.connection_by_name:
            conn = self.connection_by_name[location_name]
            a = self._world_to_screen(conn.zone_a.x, conn.zone_a.y)
            b = self._world_to_screen(conn.zone_b.x, conn.zone_b.y)
            return (a + b) / 2

        return pygame.Vector2(0, 0)

    def _zone_radius(self) -> int:
        return max(18, min(34, int(self.base_zone_radius * self.zoom)))

    # ---------- playback ----------

    def _next_turn(self) -> None:
        self.turn_index = min(self.turn_index + 1, len(self.snapshots) - 1)

    def _previous_turn(self) -> None:
        self.turn_index = max(self.turn_index - 1, 0)

    def _restart(self) -> None:
        self.turn_index = 0
        self.auto_play = False

    # ---------- styling ----------

    def _zone_color(self, zone) -> Tuple[int, int, int]:
        if zone.prefix == "start_hub":
            return COLORS["start_hub"]
        if zone.prefix == "end_hub":
            return COLORS["end_hub"]
        return COLORS.get(zone.metadata.zone_type, COLORS["normal"])

    def _conn_capacity(self, conn) -> int:
        meta = getattr(conn, "metadata", None)
        if hasattr(meta, "max_link_capacity"):
            return int(meta.max_link_capacity)
        if isinstance(meta, int):
            return meta
        return 1

    # ---------- drone placement ----------

    def _group_drones(self, snapshot: Dict[str, str]) -> Dict[str, List[str]]:
        grouped: Dict[str, List[str]] = {}
        for drone_id, location in snapshot.items():
            grouped.setdefault(location, []).append(drone_id)
        return grouped

    def _positions_in_zone(self, center: pygame.Vector2, count: int) -> List[Tuple[int, int]]:
        if count <= 1:
            return [(int(center.x), int(center.y))]

        radius = max(8, self._zone_radius() - 10)
        pts: List[Tuple[int, int]] = []
        for i in range(count):
            angle = (2 * math.pi * i) / count - math.pi / 2
            px = center.x + math.cos(angle) * radius * 0.55
            py = center.y + math.sin(angle) * radius * 0.55
            pts.append((int(px), int(py)))
        return pts

    def _positions_on_connection(self, conn_name: str, count: int) -> List[Tuple[int, int]]:
        conn = self.connection_by_name[conn_name]
        a = self._world_to_screen(conn.zone_a.x, conn.zone_a.y)
        b = self._world_to_screen(conn.zone_b.x, conn.zone_b.y)
        mid = (a + b) / 2

        dx = b.x - a.x
        dy = b.y - a.y
        length = math.hypot(dx, dy)
        if length == 0:
            return [(int(mid.x), int(mid.y))]

        # unit perpendicular vector
        nx = -dy / length
        ny = dx / length

        spacing = 12
        positions: List[Tuple[int, int]] = []
        start = -(count - 1) / 2.0

        for i in range(count):
            t = start + i
            px = mid.x + nx * t * spacing
            py = mid.y + ny * t * spacing
            positions.append((int(px), int(py)))

        return positions

    # ---------- drawing ----------

    def _draw_background(self) -> None:
        self.screen.fill(COLORS["background"])

    def _draw_connections(self) -> None:
        drawn = set()

        for zone, connections in self.graph.elements.items():
            for neighbor, conn in connections:
                if conn.name in drawn:
                    continue

                start = self._world_to_screen(conn.zone_a.x, conn.zone_a.y)
                end = self._world_to_screen(conn.zone_b.x, conn.zone_b.y)

                width = 2 if self._conn_capacity(conn) == 1 else 4
                pygame.draw.line(self.screen, COLORS["line"], start, end, width)

                mid = (start + end) / 2
                cap = self.small_font.render(
                    str(self._conn_capacity(conn)),
                    True,
                    COLORS["line_text"],
                )
                self.screen.blit(
                    cap,
                    (mid.x - cap.get_width() / 2, mid.y - 12),
                )

                drawn.add(conn.name)

    def _draw_zones(self) -> None:
        radius = self._zone_radius()

        for zone in self.graph.elements.keys():
            pos = self._world_to_screen(zone.x, zone.y)

            pygame.draw.circle(
                self.screen,
                self._zone_color(zone),
                (int(pos.x), int(pos.y)),
                radius,
            )
            pygame.draw.circle(
                self.screen,
                COLORS["outline"],
                (int(pos.x), int(pos.y)),
                radius,
                2,
            )

            # name
            label = self.font.render(zone.name, True, COLORS["text"])
            self.screen.blit(
                label,
                (pos.x - label.get_width() / 2, pos.y - radius - 22),
            )

            # cap
            cap_value = "∞" if zone.prefix in ("start_hub", "end_hub") else str(zone.metadata.max_drones)
            cap = self.small_font.render(f"cap:{cap_value}", True, COLORS["muted"])
            self.screen.blit(
                cap,
                (pos.x - cap.get_width() / 2, pos.y + radius + 4),
            )

    def _draw_drones(self, snapshot: Dict[str, str]) -> None:
        grouped = self._group_drones(snapshot)

        for location_name, drone_ids in grouped.items():
            if location_name in self.zone_by_name:
                center = self._get_coords(location_name)
                positions = self._positions_in_zone(center, len(drone_ids))
            else:
                positions = self._positions_on_connection(location_name, len(drone_ids))

            for i, drone_id in enumerate(drone_ids):
                px, py = positions[i]
                pygame.draw.circle(self.screen, COLORS["drone"], (px, py), 8)
                pygame.draw.circle(self.screen, COLORS["drone_text"], (px, py), 8, 1)

                txt = self.small_font.render(drone_id[1:], True, COLORS["drone_text"])
                self.screen.blit(
                    txt,
                    (px - txt.get_width() / 2, py - txt.get_height() / 2),
                )

    def _draw_hud(self) -> None:
        panel = pygame.Rect(14, 14, 430, 96)
        pygame.draw.rect(self.screen, COLORS["panel"], panel, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["panel_border"], panel, 1, border_radius=10)

        title = self.big_font.render(
            f"Turn {self.turn_index}/{len(self.snapshots) - 1}",
            True,
            COLORS["text"],
        )
        self.screen.blit(title, (26, 26))

        mode = "AUTO" if self.auto_play else "PAUSE"
        line1 = self.font.render(
            f"Mode: {mode}   Delay: {self.delay_ms} ms   Zoom: {self.zoom:.2f}x",
            True,
            COLORS["muted"],
        )
        self.screen.blit(line1, (26, 60))

        line2 = self.small_font.render(
            "SPACE play/pause | LEFT prev | RIGHT next | R restart`",
            True,
            COLORS["muted"],
        )
        self.screen.blit(line2, (26, 86))

    def _draw_timeline(self) -> None:
        total_steps = max(1, len(self.snapshots) - 1)

        bar_x = 40
        bar_y = self.height - 28
        bar_w = self.width - 80
        bar_h = 8

        pygame.draw.rect(
            self.screen,
            COLORS["timeline"],
            (bar_x, bar_y, bar_w, bar_h),
            border_radius=4,
        )

        progress = self.turn_index / total_steps
        fill_w = int(progress * bar_w)

        pygame.draw.rect(
            self.screen,
            COLORS["timeline_fill"],
            (bar_x, bar_y, fill_w, bar_h),
            border_radius=4,
        )

        knob_x = bar_x + fill_w
        pygame.draw.circle(
            self.screen,
            COLORS["timeline_knob"],
            (knob_x, bar_y + bar_h // 2),
            8,
        )

    def draw(self) -> None:
        self._draw_background()
        self._draw_connections()
        self._draw_zones()
        self._draw_drones(self.snapshots[self.turn_index])
        self._draw_hud()
        self._draw_timeline()
        pygame.display.flip()

    # ---------- events ----------

    def _handle_resize(self, event: pygame.event.Event) -> None:
        self.width, self.height = event.w, event.h
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        self._recompute_layout()

    def _zoom_at(self, factor: float) -> None:
        old_zoom = self.zoom
        self.zoom = max(0.45, min(2.5, self.zoom * factor))
        if self.zoom != old_zoom:
            self._clamp_camera()

    def run(self) -> None:
        dragging = False
        last_mouse = (0, 0)

        while self.running:
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_RIGHT:
                        self._next_turn()
                    elif event.key == pygame.K_LEFT:
                        self._previous_turn()
                    elif event.key == pygame.K_r:
                        self._restart()
                    elif event.key == pygame.K_UP:
                        self.delay_ms = max(100, self.delay_ms - 100)
                    elif event.key == pygame.K_DOWN:
                        self.delay_ms += 100

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        dragging = True
                        last_mouse = event.pos
                    elif event.button == 4:
                        self._zoom_at(1.1)
                    elif event.button == 5:
                        self._zoom_at(0.9)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False

                elif event.type == pygame.MOUSEMOTION and dragging:
                    mx, my = event.pos
                    lx, ly = last_mouse
                    self.camera_x += mx - lx
                    self.camera_y += my - ly
                    self._clamp_camera()
                    last_mouse = event.pos

            if self.auto_play and now - self.last_tick >= self.delay_ms:
                if self.turn_index < len(self.snapshots) - 1:
                    self._next_turn()
                else:
                    self.auto_play = False
                self.last_tick = now

            self.draw()
            self.clock.tick(60)

        pygame.quit()
