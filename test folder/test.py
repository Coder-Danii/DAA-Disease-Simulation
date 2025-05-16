import pickle
import networkx as nx
import matplotlib.pylab as plt


with open ('pos.pickle', 'rb' ) as f:
    pos=pickle.load(f)
colors=[]
pos=dict(pos)
pp={}
for n,p in pos.items():
    print(p)
    if n not in pp:
        pp[n]=p
    if n==10 :
        colors.append("red")
        break
    colors.append('blue')


print(pos[10])
G= nx.read_weighted_edgelist("graph.edgelist.gz", delimiter=",", nodetype=int)	


G=nx.subgraph(G,[0,1,2,3,4,5,6,7,8,9,10])

nx.draw(G,pp, node_size=50,node_color=colors)

plt.show()
