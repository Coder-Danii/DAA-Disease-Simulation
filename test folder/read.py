import networkx as nx
import matplotlib.pyplot as plt
import pickle 
import time
import random

G = nx.read_weighted_edgelist("graph.edgelist.gz", delimiter=",", nodetype=int)
print(G) 

color=[]

ra = random.randint(0,4999)
print(ra)
for i in range(5000):
    if i < 2000  :
        color.append("lightblue")
    else:
        color.append("red")

adi={}
pos={}

with open("pos.pickle","rb") as f:
    pos=pickle.load(f)

with open ("adjList.pickle", "rb") as f:
    adj=pickle.load(f)

print(adj)

print("Loading done")

start_time = time.time()
nx.draw(G,pos, with_labels=False, node_color=color ,node_size=50)
plt.title("Simplest Connected Graph with 4 Nodes")
plt.show()
end_time = time.time()
print(f"It took this much time:{end_time-start_time} seconds")




# Take a sample of  nodes for visualization
# sample_nodes = list(G.nodes())[:4]
# sample_graph = G.subgraph([1250, 1251, 1252, 1253, 1254,1,2,5,3,32,341,34,3,13,4343,])
# G=sample_graph
# print(G.nodes())
# print(G.edges())


# Take a sample of  nodes for visualization
# sample_nodes = list(G.nodes())[:20]  
# sample_graph = G.subgraph(sample_nodes)
# G=sample_graph
