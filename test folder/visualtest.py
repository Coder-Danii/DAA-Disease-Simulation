import networkx as nx
import matplotlib.pyplot as plt
import pickle 
import numpy as np
from vispy import app, scene
from vispy.scene.visuals import Markers
import queue

import random
from vispy.app import Timer
import math 
temp_infected = []

positions=[]
i=0
adj=None
colors=None
sizes = np.ones(5000) * 10  # default size 10
is_at_risk = np.zeros(5000, dtype=int)
scatter=None
view=None
steps = 60 # Number of frames for the animation
current_step = [0]
start_x = 0
end_x = 0
start_y = 0
end_y = 0
target_xmin, target_xmax = [0,0]
target_ymin, target_ymax = [0,0]
infected=[]
infected_count=-1
to_zoom=0
infected_color=[1,0,0,1]
interaction_color=[1,0,0,1]
non_infected_color=[0, 1, 0, 0.3]
at_risk_color=[0, 0.3, 1, 1]
is_infected=np.zeros(5000, dtype=bool)
is_alive=np.ones(5000, dtype=bool)
move_count=[]
move_timer=None
original_positions = None
move_indices = None
move_midpoint = None
move_steps = 30
new_positions = None
move_current_step = [0]
move_phase = [1]  # 1: moving to midpoint, 2: moving back
G={}
idx1=0
idx2=0
inf_prob=1
pos1_orig=None
pos2_orig=None
midpoints=None
max_inf_degree=20
new_scatter=None

to_process = [queue.Queue() for _ in range(5000)]  

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
    global is_infected,infected,max_inf_degree,infected_count, colors,scatter,view,target_xmin, target_xmax, target_ymin, target_ymax, timer
    canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='black', fullscreen=True)
    canvas.show()
    view = canvas.central_widget.add_widget(scene.widgets.ViewBox())
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

    


    for i in infected:
        for node in adj[i]:
            colors[node[0]] = at_risk_color
    
    for i in infected:
        colors[i] = infected_color
        is_infected[i] = True
        


    scatter = Markers(parent=view)
    scatter.set_data(positions, face_color=colors, size=sizes, edge_color=None)

    view.add(scatter)
    
    view.camera = scene.PanZoomCamera(aspect=1)
    view.camera.set_range(x=(start_x, end_x), y=(start_y, end_y))
    
    global delay_timer
    delay_timer = Timer(interval=2.0, iterations=1, connect=wait_two, start=True)   

def smooth_zoom(event):
    global start_x, end_x, start_y, end_y,to_zoom,steps
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
        scatter.set_data(positions, face_color=colors, size=sizes , edge_color=None)
        start_x = x0
        end_x = x1
        start_y = y0
        end_y = y1
        current_step[0] = 0

        if to_zoom == 0:
            to_zoom = 1
            global delay_timer
            # Start zoom after 2 seconds
            delay_timer = Timer(interval=1, iterations=1, connect=start_zoom, start=True)

        elif to_zoom == 1:
            to_zoom = 2
            print("the infected node is", infected[0])

            for x in adj[infected[0]]:
                to_process[infected[0]].put(x)
                print("The node is", x[0])
                is_at_risk[x[0]] = +1

            # Delay the node meeting animation slightly to allow zoom to finish
            delay_timer = Timer(interval=0, iterations=1, connect=start_node_meeting_animation, start=True)

        elif to_zoom < 9:
            steps = 60 - to_zoom * 5
            # Run the next step after a short delay
            delay_timer = Timer(interval=0, iterations=1, connect=start_node_meeting_animation, start=True)


    


def start_zoom(event=None):
    global  target_xmin, target_xmax, target_ymin, target_ymax
    rel = []
    temp_count = infected_count
    for idx in infected:
        rel.extend(adj[idx])
        rel_x = []
        rel_y = []
        # temp_count += 1
    
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
    delay_timer = Timer(interval=0, iterations=1, connect=wait_two, start=True)
      
      
def wait_two(event):
    global timer
    timer = Timer(interval=0.016, connect=smooth_zoom, start=True)  # ~180 
    
  
def start_smooth_zoom(event=None):
    global timer
    timer = Timer(interval=0.016, connect=smooth_zoom, start=True)  # ~60 FPS

def start_smooth_zoom_again(event=None):
    global timer
    timer = Timer(interval=0.016, connect=smooth_zoom, start=True)  
def start_node_meeting_animation(event=None):
    global temp_infected ,original_positions,i,max_inf_degree,move_count, move_indices, move_midpoint, move_current_step, move_phase,inf_prob
    temp_infected = []
    move_indices = []
    move_midpoint =[]
    original_positions = []

    
    calculate_move_positions()
    if len(move_indices) == 0:
        # No nodes to move, just return
        return
    move_current_step[0] = 0
    move_phase[0] = 1  
    global move_timer
    move_timer = Timer(interval=0.016, connect=move_nodes_meeting, start=True)

    

                
           

def calculate_move_positions():
    global positions,infected,infected_count,temp_infected, scatter, move_indices, original_positions, move_midpoint, move_current_step, move_phase, move_timer,idx1, idx2, pos1_orig, pos2_orig, midpoints
    temp_infected = []
    for i in range(5000):
        if to_process[i].empty() or not is_alive[i]:
            continue
        else:
            x=to_process[i].get()
            if not is_alive[x[0]]:
                continue
            if to_process[i].empty():
                for node in adj[x[0]]:
                        to_process[x[0]].put(node)
                        is_at_risk[node[0]] = +1
            ra=random.randint(1,10)
            if ra+10 < x[1]:
                continue
            ira = random.uniform(0, 1)
            if ira < inf_prob:
                if is_infected[x[0]] == False :
                    is_infected[x[0]] = True
                    

                    temp_infected.append(x[0])
                    for node in adj[x[0]]:
                        to_process[x[0]].put(node)
    
                    
            move_indices.append((x[0],i))
            move_midpoint.append((positions[x[0]] + positions[i]) / 2)
            original_positions.append((positions[x[0]].copy(), positions[i].copy()))
            



            
            # if is_infected[x] == False:
            #     is_infected[x] = True
            #     temp_infected.append(x)
            #     colors[x] = at_risk_color

    
     
    idx1 = np.array([pair[0] for pair in move_indices], dtype=int)
    idx2 = np.array([pair[1] for pair in move_indices], dtype=int)
    pos1_orig = np.array([pair[0] for pair in original_positions])
    pos2_orig = np.array([pair[1] for pair in original_positions])
    midpoints = np.array(move_midpoint)


death_prob = 0.5
recovery_time=14
def death_check(event=None):
    i=0
    global is_alive,infected_count,positions,colors,scatter ,sizes
    while i<infected_count:
        x=infected[i]
        print("THe index is",i)
        print("the infected_count is",infected_count)
        i+=1
        if random.uniform(0, 1) <death_prob:  # 5% chance of death
            is_alive[x] = False
            sizes[x] = 0
            for node in adj[x]:
                    if is_infected[node[0]] == False and is_alive[node[0]] == True and is_at_risk[node[0]] >0:
                        colors[node[0]] = non_infected_color
            is_at_risk[x]-= 1
            infected.remove(x)
            infected_count-= 1
            scatter.set_data(positions, face_color=colors, size=sizes , edge_color=None)
            print("dead",x) 
            

def move_nodes_meeting(event):
    global delay_timer,colors,temp_infected,move_timer,i, positions,new_scatter,view, scatter,move_count, idx1, idx2, pos1_orig, pos2_orig, midpoints,move_phase,infected_count
    steps = move_steps

    if move_current_step[0] <= steps :
        
        t = move_current_step[0] / steps
        if move_phase[0] == 1:
            # Move toward the midpoint
            positions[idx1] = (1 - t) * pos1_orig + t * midpoints
            positions[idx2] = (1 - t) * pos2_orig + t * midpoints
        else:
            # Move back to original positions
            positions[idx1] = (1 - t) * midpoints + t * pos1_orig
            positions[idx2] = (1 - t) * midpoints + t * pos2_orig

        scatter.set_data(positions, face_color=colors, size=sizes, edge_color=None)
        move_current_step[0] += 1
    else:
        move_current_step[0] = 0
        if move_phase[0] == 1:
            move_timer.stop()  # Stop the movement animation
            for x in temp_infected:
                colors[x] = infected_color
                for node in adj[x]:
                    if is_infected[node[0]] == False:

                        colors[node[0]] = at_risk_color
            
            infected.extend(temp_infected)
            infected_count += len(temp_infected)
        
            
            scatter_graph_on_midpoints()
            blink_and_remove_new_scatter(callback=resume_node_animation)
            move_phase[0] = 2  # Switch to moving back
            view.add(new_scatter)

        else:
            move_timer.stop()
            delay_timer = Timer(interval=0.5, iterations=1, connect=death_check, start=True)
            
            delay_timer = Timer(interval=0, iterations=1, connect=start_zoom, start=True)
              # Stop the timer after moving back
            # start_node_meeting_animation()
            # if i < max_inf_degree - 1:
            #     i += 1
            #     start_node_meeting_animation()
            # else:
            #     i=0
            #     temp_infected = []
            #     start_node_meeting_animation()

                
           
def resume_node_animation():
    global move_timer
    move_timer = Timer(interval=0.016, connect=move_nodes_meeting, start=True)


def scatter_graph_on_midpoints():
    global view, midpoints, new_scatter, new_positions
    # Remove previous overlay scatter if it exists
    if new_scatter is not None:
        new_scatter.parent = None
        new_scatter = None

    new_positions = np.array(midpoints)
    num_new = len(new_positions)
    new_colors = np.array([interaction_color] * num_new)

    new_scatter = scene.visuals.Markers(parent=view)
    new_scatter.set_gl_state(depth_test=False)
    new_scatter.set_data(new_positions, face_color=new_colors, size=15, edge_color=None)

    
 


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
    