from pyvis.network import Network
import networkx as nx
import random

# Generate a random graph with 10,000 nodes and ~20,000 edges
num_nodes = 10000
num_edges = 20000

G = nx.Graph()
G.add_nodes_from(range(num_nodes))

for _ in range(num_edges):
    u = random.randint(0, num_nodes - 1)
    v = random.randint(0, num_nodes - 1)
    if u != v:
        G.add_edge(u, v)

# Create a PyVis network
net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")

# Load the NetworkX graph into PyVis
net.from_nx(G)

# Disable physics for large graphs
net.toggle_physics(False)

# Save and view
net.show("large_graph.html")
