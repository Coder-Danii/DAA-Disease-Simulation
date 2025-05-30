import random
import pickle

def custom_spring_layout(G, iterations=50, width=1.0, height=1.0, k=None, seed=None):
    if seed is not None:
        random.seed(seed)
    
    nodes = list(G.keys())
    n = len(nodes)
    
    if k is None:
        k = math.sqrt(width * height / n)

    # Initialize positions randomly
    pos = {node: [random.uniform(0, width), random.uniform(0, height)] for node in nodes}
    disp = {node: [0, 0] for node in nodes}
    
    
    for _ in range(iterations):
        # Reset displacement
        for v in nodes:
            disp[v] = [0, 0]

        # Repulsive forces
        for v in nodes:
            for u in nodes:
                if u != v:
                    dx = pos[v][0] - pos[u][0]
                    dy = pos[v][1] - pos[u][1]
                    distance = math.hypot(dx, dy) + 1e-6  # prevent divide by zero
                    force = k**2 / distance
                    disp[v][0] += (dx / distance) * force
                    disp[v][1] += (dy / distance) * force

        # Attractive forces
        for v in nodes:
            for u_data in G[v]:
                u = u_data[0]
                if u > v:  # Avoid double counting since the graph is undirected
                    dx = pos[v][0] - pos[u][0]
                    dy = pos[v][1] - pos[u][1]
                    distance = math.hypot(dx, dy) + 1e-6
                    force = (distance**2) / k
                    fx = (dx / distance) * force
                    fy = (dy / distance) * force
                    disp[v][0] -= fx
                    disp[v][1] -= fy
                    disp[u][0] += fx
                    disp[u][1] += fy

        # Limit max displacement and update positions
        for v in nodes:
            dx, dy = disp[v]
            disp_mag = math.hypot(dx, dy)
            if disp_mag > 0:
                dx = dx / disp_mag * min(disp_mag, 0.1)
                dy = dy / disp_mag * min(disp_mag, 0.1)
            pos[v][0] = min(width, max(0, pos[v][0] + dx))
            pos[v][1] = min(height, max(0, pos[v][1] + dy))

    return pos
def watts_strogatz_graph(n, k, p, seed=None):
    if seed is not None:
        random.seed(seed)

    G = {node: [] for node in range(n)}

    # Step 1: Ring lattice
    for node in range(n):
        for i in range(1, k // 2 + 1):
            neighbor = (node + i) % n
            if not is_connected(G, node, neighbor):
                G[node].append([neighbor, None])
                G[neighbor].append([node, None])

    # Step 2: Rewiring
    for node in range(n):
        for i in range(1, k // 2 + 1):
            neighbor = (node + i) % n
            if random.random() < p:
                # Find the edge in the list
                remove_edge(G, node, neighbor)

                possible_targets = set(range(n)) - {node} - {x[0] for x in G[node]}
                if possible_targets:
                    new_neighbor = random.choice(list(possible_targets))
                    G[node].append([new_neighbor, None])
                    G[new_neighbor].append([node, None])

    # Step 3: Assign weights
    for node in G:
        for i in range(len(G[node])):
            neighbor, weight = G[node][i]
            if weight is None:
                random_weight = random.randint(1, 10)
                G[node][i][1] = random_weight
                # Update the corresponding entry in the neighbor
                for j in range(len(G[neighbor])):
                    if G[neighbor][j][0] == node:
                        G[neighbor][j][1] = random_weight
                        break
    
    return G

if __name__=='__main__':
    n=5000
    k=10
    p=0.05
    G=watts_strogatz_graph(n, k, p, seed=None)
    
    print("It started")
    pos=custom_spring_layout(G)
    print("Dumping")
    with open ("pos_1.pickle",'wb') as f:
        pickle.dump(pos,f)
    with open ("adjList_1.pickle","wb") as f:
        pickle.dump(G,f)
