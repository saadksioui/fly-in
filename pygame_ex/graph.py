from queue import PriorityQueue

graph = {
        'A': [('B', 3), ('C', 6), ('D', 4)],
        'B': [('A', 3), ('C', 2), ('E', 3)],
        'C': [('A', 6), ('B', 2), ('E', 3), ('F', 3)],
        'D': [('A', 4), ('F', 6)],
        'E': [('B', 3), ('C', 3), ('F', 1)],
        'F': [('D', 6), ('C', 3), ('E', 1)]
}



def dijkstra(graph, start):
    distances = {v: float('inf') for v in graph.keys()}
    visited = {v: False for v in graph.keys()}
    previous = {v: None for v in graph.keys()}
    distances[start] = 0
    pq = PriorityQueue()
    pq.put((distances[start], start))
    while not pq.empty():
        weight, node = pq.get()
        visited[node] = True
        for n, w in graph[node]:
            if not visited[n]:
                new_d = w + weight
                if new_d < distances[n]:
                    distances[n] = new_d
                    previous[n] = node
                    pq.put((distances[n], n))
    return previous

prev = dijkstra(graph, 'A')
path = []
curr = 'F'
while curr is not None:
    path.append(curr)
    curr = prev[curr]
path.reverse()
print("->".join(path))


