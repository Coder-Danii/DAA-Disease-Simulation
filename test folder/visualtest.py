import networkx as nx
import matplotlib.pyplot as plt
import pickle 
import numpy as np
from vispy import app, scene
import random
from vispy.app import Timer
import math 
positions=[]
i=0
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
infected_count=-1
to_zoom=True
infected_color=[1,0,0,1]
interaction_color=[1,1,0,1]
non_infected_color=[0.8, 1, 0.8, 1] 
at_risk_color=[0, 0.3, 1, 1]
is_infected=None
is_alive=None
move_count=[]
move_timer=None
original_positions = None
move_indices = None
move_midpoint = None
move_steps = 60
new_positions = None
move_current_step = [0]
move_phase = [1]  # 1: moving to midpoint, 2: moving back
G={}
idx1=0
idx2=0

pos1_orig=None
pos2_orig=None
midpoints=None
max_inf_degree=0
new_scatter=None
def load_data():
    global G,positions,adj,start_x,end_x,start_y,end_y,infected, infected_count, target_xmin, target_xmax, target_ymin, target_ymax
    G = nx.read_weighted_edgelist("graph.edgelist.gz", delimiter=",", nodetype=int)

    with open("pos.pickle","rb") as f:
        pos=pickle.load(f)
    with open ("adjList.pickle", "rb") as f:
        adj=pickle.load(f)
       
    positions = np.array([pos[node] for node in pos])

    is_infected = np.zeros(len(positions), dtype=bool)
    is_alive = np.ones(len(positions), dtype=bool)
    start_x = positions[:,0].min()
    end_x = positions[:,0].max()
    start_y = positions[:,1].min()
    end_y = positions[:,1].max()

def start():
    global infected,max_inf_degree,infected_count, colors,scatter,view,target_xmin, target_xmax, target_ymin, target_ymax, timer
    canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='white', fullscreen=True)
    view = canvas.central_widget.add_view()
    # Scatter plot (circles)
    colors = np.array([non_infected_color] * len(positions))

    idx= random.randint(0,(len(positions)-1))
    x, y = positions[idx]
    infected.append(idx)
    if max_inf_degree < G.degree(idx):
        max_inf_degree = G.degree(idx)
    infected_count+=1
    target_xmin, target_xmax = x-0.05, x+0.05
    target_ymin, target_ymax = y-0.05, y+0.05
    timer = 0

    colors[idx] = infected_color
    for i in infected:
        for node in adj[i]:
            colors[node[0]] = at_risk_color
    for node in adj[infected[0]]:
        colors[node[0]] = at_risk_color


    scatter = scene.visuals.Markers()
    scatter.set_data(positions, face_color=colors, size=5, edge_color=None)

    view.add(scatter)
    
    view.camera = scene.PanZoomCamera(aspect=1)
    view.camera.set_range(x=(start_x, end_x), y=(start_y, end_y))
    
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
        else:
            start_node_meeting_animation()

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
      
def wait_two(event):
    global timer
    timer = Timer(interval=0.016, connect=smooth_zoom, start=True)  # ~180 
    


def start_node_meeting_animation():
    global original_positions,i,max_inf_degree,move_count, move_indices, move_midpoint, move_current_step, move_phase

    # Pick two random nodes
    move_indices = []
    move_midpoint =[]
    original_positions = []
    print("infected", infected)
    for x in infected:
        if i < len(adj[x]):
            print("this is i", i)
            move_indices.append((x,adj[x][i][0]))
            move_midpoint.append((positions[x] + positions[adj[x][i][0]]) / 2)
            original_positions.append((positions[x].copy(), positions[adj[x][i][0]].copy()))
    print(move_indices)
    
    if not move_indices:
        return
    
    move_current_step[0] = 0
    move_phase[0] = 1  
    calculate_move_positions()
    print(move_phase)
    global move_timer
    move_timer = Timer(interval=0.016, connect=move_nodes_meeting, start=True)

def calculate_move_positions():
    global positions, scatter, move_indices, original_positions, move_midpoint, move_current_step, move_phase, move_timer,idx1, idx2, pos1_orig, pos2_orig, midpoints

    idx1 = np.array([pair[0] for pair in move_indices], dtype=int)
    idx2 = np.array([pair[1] for pair in move_indices], dtype=int)
    pos1_orig = np.array([pair[0] for pair in original_positions])
    pos2_orig = np.array([pair[1] for pair in original_positions])
    midpoints = np.array(move_midpoint)


def move_nodes_meeting(event):
    global move_timer,i, positions,new_scatter,view, scatter,move_count, idx1, idx2, pos1_orig, pos2_orig, midpoints,move_phase
    steps = move_steps

    if move_current_step[0] <= steps:
        
        t = move_current_step[0] / steps
        if move_phase[0] == 1:
            # Move toward the midpoint
            positions[idx1] = (1 - t) * pos1_orig + t * midpoints
            positions[idx2] = (1 - t) * pos2_orig + t * midpoints
        else:
            # Move back to original positions
            positions[idx1] = (1 - t) * midpoints + t * pos1_orig
            positions[idx2] = (1 - t) * midpoints + t * pos2_orig

        scatter.set_data(positions, face_color=colors, size=10, edge_color=None)
        move_current_step[0] += 1
    else:
        move_current_step[0] = 0
        if move_phase[0] == 1:
            move_timer.stop()  # Stop the movement animation
            scatter_graph_on_midpoints()
            blink_and_remove_new_scatter(callback=resume_node_animation)
            move_phase[0] = 2  # Switch to moving back
            view.add(new_scatter)

        else:
            move_timer.stop()  # Stop the timer after moving back
            if i < max_inf_degree + 1:
                i += 1
                start_node_meeting_animation()
                
           
def resume_node_animation():
    global move_timer
    move_timer = Timer(interval=0.016, connect=move_nodes_meeting, start=True)


def scatter_graph_on_midpoints():
    global view, midpoints, new_scatter,new_positions
    # Make sure midpoints is a NumPy array of shape (N, 2)
    new_positions = np.array(midpoints)
    num_new = len(new_positions)

    # Choose a color for the new graph nodes (e.g., black)
    new_colors = np.array([[0, 0, 0, 1]] * num_new)

    # Create a new Markers visual for the new graph
    new_scatter = scene.visuals.Markers()
    new_scatter.set_data(new_positions, face_color=interaction_color, size=15, edge_color=None)

    
 


def blink_and_remove_new_scatter(callback=None):
    global new_scatter, view, blink_timer,new_positions

    blink_duration = 2.0  # seconds
    interval = 0.016      # ~60 FPS
    total_steps = int(blink_duration / interval)
    step = [0]

    def blink(event):
        
        # Animate size using a sine wave for smooth blinking
        # Calmer blinking: smaller amplitude and slower frequency
        base_size = 15
        amplitude = 10  # was 10, now less extreme
        period = 45    # was 30, now slower (higher = slower blink)
        blink_size = base_size + amplitude * abs(math.sin(2 * math.pi * step[0] / period))

        new_scatter.set_data(new_scatter._data['a_position'], face_color=interaction_color, size=blink_size, edge_color=None)

        step[0] += 1

        if step[0] >= total_steps:
            # Remove the scatter after blinking
            
            new_scatter.parent = None  # Remove from scene
            
            blink_timer.stop()
            if callback:
                callback()

    blink_timer = Timer(interval=interval, connect=blink, start=True)

if __name__ == '__main__':
    
    load_data()
    start()
    app.run()
    