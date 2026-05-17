from typing import List
from src.data import Graph
import pygame


class Visualization:
    def __init__(self, graph: Graph, logs: List[str]) -> None:
        self.graph = graph
        self.logs = logs
