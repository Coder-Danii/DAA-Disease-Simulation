import networkx as nx
import random
import pickle


# n=10000       n=5000      
# k=12          k=10
# p=0.05


# G=nx.watts_strogatz_graph(n,k,p,seed=17)

print("Start")

G=nx.barabasi_albert_graph(5000,3,seed=17)

print("Graph generated")

for u,v in G.edges():
    G[u][v]['weight']=random.randint(1,10)

print("Weights added")

pos= nx.spring_layout(G,seed=17)

print("layout done")

with open ("pos.pickle",'wb') as f:
    pickle.dump(pos,f)

# adj list
adj = {node: [] for node in G.nodes()}
for edges in G.edges():
    weight=G[edges[0]][edges[1]]['weight']
    adj[edges[0]].append([edges[1],weight])
    adj[edges[1]].append([edges[0],weight])
with open ("adjList.pickle","wb") as f:
    pickle.dump(adj,f)


print("dump done")

nx.write_weighted_edgelist(G, "graph.edgelist.gz", delimiter=",")

print("saved to graph.edgelist.gz")

print(G)
