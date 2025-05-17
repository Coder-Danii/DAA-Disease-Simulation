import networkx as nx
import matplotlib.pyplot as plt
import pickle 
import numpy as np
from vispy import app, scene
import time
import random
from vispy.app import Timer
positions=[]
adj=None
colors=None
scatter=None
view=None
steps = 180 # Number of frames for the animation
current_step = [0]
start_x = 0
end_x = 0
start_y = 0
end_y = 0
target_xmin, target_xmax = [0,0]
target_ymin, target_ymax = [0,0]
infected=[]
to_zoom=True
infected_color=[1,0,0,1]
non_infected_color=[0.8, 1, 0.8, 1] 
at_risk_color=[0, 0.3, 1, 1]

def load_data():
    global positions,adj,start_x,end_x,start_y,end_y
    G = nx.read_weighted_edgelist("graph.edgelist.gz", delimiter=",", nodetype=int)

    with open("pos.pickle","rb") as f:
        pos=pickle.load(f)
    with open ("adjList.pickle", "rb") as f:
        adj=pickle.load(f)
    positions = np.array([pos[node] for node in pos])
    start_x = positions[:,0].min()
    end_x = positions[:,0].max()
    start_y = positions[:,1].min()
    end_y = positions[:,1].max()
def start():
    global infected, colors,scatter,view,target_xmin, target_xmax, target_ymin, target_ymax, timer
    canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='white', fullscreen=True)
    view = canvas.central_widget.add_view()
    # Scatter plot (circles)
    colors = np.array([non_infected_color] * len(positions))

    idx= random.randint(0,(len(positions)-1))
    x, y = positions[idx]
    infected.append(idx)   
    target_xmin, target_xmax = x-0.05, x+0.05
    target_ymin, target_ymax = y-0.05, y+0.05
   
    timer = 0

    colors[idx] = infected_color
    for node in adj[infected[0]]:
        colors[node[0]] = at_risk_color


    scatter = scene.visuals.Markers()
    scatter.set_data(positions, face_color=colors, size=5, edge_color=None)
    view.add(scatter)
    
    view.camera = scene.PanZoomCamera(aspect=1)
    view.camera.set_range(x=(start_x, end_x), y=(start_y, end_y))
    
    global delay_timer
    delay_timer = Timer(interval=2.0, iterations=1, connect=wait_two, start=True)    
    

def start_zoom():
    global  target_xmin, target_xmax, target_ymin, target_ymax
    rel = []
    for idx in infected:
        rel.extend(adj[idx])
    rel_x = []
    rel_y = []
    for i in rel:
        rel_x.append(positions[i[0]][0])
        rel_y.append(positions[i[0]][1])
    rel_x = np.array(rel_x)
    rel_y = np.array(rel_y)
    rmin_x, rmax_x = min(rel_x[:]),max(rel_x[:])
    rmin_y, rmax_y = min(rel_y[:]),max(rel_y[:])
    target_xmin, target_xmax = min(target_xmin, rmin_x),max(target_xmax, rmax_x)
    target_ymin, target_ymax = min(target_ymin, rmin_y),max(target_ymax, rmax_y)

    global delay_timer
    delay_timer = Timer(interval=2.0, iterations=1, connect=wait_two, start=True)    

def smooth_zoom(event):
    global start_x, end_x, start_y, end_y,to_zoom
    t = current_step[0] / steps
    # Linear interpolation
    x0 = (1-t)*start_x + t*target_xmin
    x1 = (1-t)*end_x + t*target_xmax
    y0 = (1-t)*start_y + t*target_ymin
    y1 = (1-t)*end_y + t*target_ymax
    view.camera.set_range(x=(x0, x1), y=(y0, y1))
    current_step[0] += 1
    if current_step[0] > steps:
        timer.stop()
        scatter.set_data(positions, face_color=colors, size=10 , edge_color=None)
        start_x = x0
        end_x = x1
        start_y = y0
        end_y = y1
        current_step[0] = 0

        if to_zoom:
            to_zoom = False
            start_zoom()
            
        
        

def wait_two(event):
    global timer
    
    timer = Timer(interval=0.016, connect=smooth_zoom, start=True)  # ~180 FPS
    

if __name__ == '__main__':
    
    load_data()
    start()
    
    
    app.run()
    