from collections import deque
import time
from queue import PriorityQueue


def get_time(function):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        print(f"Time of running: {(end_time - start_time):.2f}")
        return result
    return wrapper


# Graph Traversal

def dfsprint(graph, start):
    stack = [start]
    while len(stack) > 0:
        current = stack.pop()
        print(current)
        for neighbor in graph[current]:
            stack.append(neighbor)


def bfsprint(graph, start):
    queue = deque(start)
    while len(queue) > 0:
        current = queue.pop()
        print(current)
        for neighbor in graph[current]:
            queue.appendleft(neighbor)


# Graph Search

@get_time
def dfspath(graph, visited, start, end):
    stack = [start]
    while len(stack) > 0:
        current = stack.pop()
        if current == end:
            return True
        for neighbor in graph[current]:
            if visited[neighbor] is False:
                stack.append(neighbor)
    return False


@get_time
def bfspath(graph, start, end):
    queue = deque(start)
    while len(queue) > 0:
        current = queue.pop()
        if current == end:
            return True
        for neighbor in graph[current]:
            queue.appendleft(neighbor)
    return False


def component_count(graph):
    count = 0
    visited = set()
    for node in graph:
        if node in visited:
            continue
        count += 1
        stack = [node]
        while stack:
            current = stack.pop()
            print(current, end=" ")
            if current not in visited:
                visited.add(current)
                for neighbor in graph[current]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        print()    
    return count


def dijkstra(graph, start):
    distance = {v: float('inf') for v in graph.keys()}
    previous = {v: None for v in graph.keys()}
    visited = {v: False for v in graph.keys()}
    distance[start] = 0
    pq = PriorityQueue()
    pq.put((start, distance[start]))
    while not pq.empty():
        vertex, weight = pq.get()
        print(f"Vertex: {vertex}, Weight: {weight}")
        visited[vertex] = True
        for v, w in graph[vertex]:
            if not visited[v]:
                new_distance = w + weight
                if new_distance < distance[v]:
                    distance[v] = weight + w
                    previous[v] = vertex
                    pq.put((v, distance[v]))
    return (distance, previous)



if __name__ == "__main__":
    # graph = {
    #     'a': ['c', 'f', 'g'],
    #     'c': ['d'],
    #     'd': ['b'],
    #     'b': [],
    #     'g': [],
    #     'f': ['e'],
    #     'e': []
    # }
    # print("Graph Traversal:")
    # print("DFS: ", end="")
    # dfsprint(graph, 'a')
    # print("\nBFS: ", end="")
    # bfsprint(graph, 'a')
    # print("Graph Search:")
    # print(f"DFS: {dfspath(graph, 'a', 'e')}")
    # print(f"BFS: {bfspath(graph, 'a', 'e')}")
    graph = {
        'A': [('B', 3), ('C', 6), ('D', 4)],
        'B': [('A', 3), ('C', 2), ('E', 3)],
        'C': [('A', 6), ('B', 2), ('E', 3), ('F', 3)],
        'D': [('A', 4), ('F', 6)],
        'E': [('B', 3), ('C', 3), ('F', 1)],
        'F': [('D', 6), ('C', 3), ('E', 1)]
        }
    print(dijkstra(graph, 'A'))
#    graph = {
#        1: [2],
#        2: [1],
#        3: [],
#        4: [6],
#        5: [6],
#        6: [4, 5, 7, 8],
#        7: [6],
#        8: [6]
#    }
#result = component_count(graph)
#print(result)
