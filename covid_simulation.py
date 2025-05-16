import numpy as np
from vispy import app, scene
import random
import math
from vispy.color import Color

# Simulation parameters
NUM_NODES = 25
BASE_RADIUS = 8
INFECTION_PROB = 0.7
INTERACTION_TIME = 2.0
APPROACH_SPEED = 0.5
MIN_DISTANCE = 50
WIDTH, HEIGHT = 1000, 800

class Person:
    def __init__(self, x, y, id):
        self.id = id
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.radius = BASE_RADIUS
        self.infected = False
        self.color = Color('green')
        self.pulse_phase = 0
        self.pulse_size = 0
        
    def update(self, dt):
        if self.pulse_size > 0:
            self.pulse_phase += dt * 10
            self.radius = BASE_RADIUS + math.sin(self.pulse_phase) * self.pulse_size
            self.pulse_size = max(0, self.pulse_size - dt * 2)
        else:
            self.radius = BASE_RADIUS
            
    def start_pulse(self):
        self.pulse_size = 5

class Interaction:
    def __init__(self, person1, person2):
        self.p1 = person1
        self.p2 = person2
        self.progress = 0
        self.phase = "approach"
        self.time_elapsed = 0
        self.completed = False
        
    def update(self, dt):
        if self.phase == "approach":
            self.progress = min(1, self.progress + APPROACH_SPEED * dt)
            
            mid_x = (self.p1.base_x + self.p2.base_x) / 2
            mid_y = (self.p1.base_y + self.p2.base_y) / 2
            
            self.p1.x = self.p1.base_x + (mid_x - self.p1.base_x) * self.progress
            self.p1.y = self.p1.base_y + (mid_y - self.p1.base_y) * self.progress
            self.p2.x = self.p2.base_x + (mid_x - self.p2.base_x) * self.progress
            self.p2.y = self.p2.base_y + (mid_y - self.p2.base_y) * self.progress
            
            if self.progress >= 1:
                self.phase = "interact"
                self.p1.start_pulse()
                self.p2.start_pulse()
                
        elif self.phase == "interact":
            self.time_elapsed += dt
            if self.time_elapsed >= INTERACTION_TIME:
                self.phase = "retreat"
                if (self.p1.infected and not self.p2.infected and 
                    random.random() < INFECTION_PROB):
                    self.p2.infected = True
                    self.p2.color = Color('red')
                elif (self.p2.infected and not self.p1.infected and 
                      random.random() < INFECTION_PROB):
                    self.p1.infected = True
                    self.p1.color = Color('red')
                    
        elif self.phase == "retreat":
            self.progress = max(0, self.progress - APPROACH_SPEED * dt)
            
            mid_x = (self.p1.base_x + self.p2.base_x) / 2
            mid_y = (self.p1.base_y + self.p2.base_y) / 2
            
            self.p1.x = self.p1.base_x + (mid_x - self.p1.base_x) * self.progress
            self.p1.y = self.p1.base_y + (mid_y - self.p1.base_y) * self.progress
            self.p2.x = self.p2.base_x + (mid_x - self.p2.base_x) * self.progress
            self.p2.y = self.p2.base_y + (mid_y - self.p2.base_y) * self.progress
            
            if self.progress <= 0:
                self.completed = True
                self.p1.x, self.p1.y = self.p1.base_x, self.p1.base_y
                self.p2.x, self.p2.y = self.p2.base_x, self.p2.base_y

class COVIDSimulator:
    def __init__(self):
        # Create a scene
        self.scene = scene.SceneCanvas(keys='interactive', size=(WIDTH, HEIGHT), show=True)
        self.view = self.scene.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(rect=(0, 0, WIDTH, HEIGHT))
        
        # Create people with minimum spacing
        self.people = []
        for i in range(NUM_NODES):
            while True:
                x = random.randint(50, WIDTH-50)
                y = random.randint(50, HEIGHT-50)
                
                valid = True
                for p in self.people:
                    if math.dist((x, y), (p.x, p.y)) < MIN_DISTANCE:
                        valid = False
                        break
                        
                if valid:
                    self.people.append(Person(x, y, i))
                    break
        
        # Create connections between people
        self.connections = []
        for i in range(NUM_NODES):
            for j in range(i+1, NUM_NODES):
                if random.random() < 0.1:
                    self.connections.append((i, j))
        
        # Infect random patient zero
        patient_zero = random.choice(self.people)
        patient_zero.infected = True
        patient_zero.color = Color('red')
        
        # Create initial interactions
        self.interactions = []
        for i, j in self.connections:
            p1, p2 = self.people[i], self.people[j]
            if p1.infected or p2.infected:
                if p1.infected != p2.infected:
                    self.interactions.append(Interaction(p1, p2))
        
        # Create visuals
        self.node_pos = np.array([[p.x, p.y] for p in self.people])
        self.node_colors = np.array([p.color.rgba for p in self.people])
        self.node_sizes = np.array([p.radius * 2 for p in self.people])
        
        # Connection lines
        self.connection_lines = []
        for i, j in self.connections:
            p1, p2 = self.people[i], self.people[j]
            line = scene.Line(pos=np.array([[p1.base_x, p1.base_y], [p2.base_x, p2.base_y]]),
                            color=Color('gray').rgba,
                            connect='segments',
                            method='gl',
                            parent=self.view.scene)
            line.set_gl_state('translucent', depth_test=False)
            self.connection_lines.append(line)
        
        # Active interaction lines
        self.active_interaction_lines = []
        
        # Nodes
        self.nodes = scene.Markers(pos=self.node_pos,
                                 face_color=self.node_colors,
                                 size=self.node_sizes,
                                 parent=self.view.scene)
        
        # Text
        self.text = scene.Text('', pos=(20, 20), color='white', parent=self.view.scene)
        
        # Timer
        self.timer = app.Timer(1/60., connect=self.on_timer)
        self.timer.start()
    
    def on_timer(self, event):
        dt = 1/60.  # Fixed timestep for simplicity
        
        # Update all people
        for person in self.people:
            person.update(dt)
        
        # Update node visuals
        self.node_pos = np.array([[p.x, p.y] for p in self.people])
        self.node_colors = np.array([p.color.rgba for p in self.people])
        self.node_sizes = np.array([p.radius * 2 for p in self.people])
        self.nodes.set_data(pos=self.node_pos,
                          face_color=self.node_colors,
                          size=self.node_sizes)
        
        # Update interactions
        active_interactions = []
        new_infections = []
        
        for interaction in self.interactions[:]:
            interaction.update(dt)
            
            if not interaction.completed:
                active_interactions.append(interaction)
            else:
                self.interactions.remove(interaction)
                
                if interaction.p1.infected and interaction.p1.color == Color('red'):
                    new_infections.append(interaction.p1)
                if interaction.p2.infected and interaction.p2.color == Color('red'):
                    new_infections.append(interaction.p2)
        
        # Create new interactions for newly infected
        for infected in new_infections:
            for i, j in self.connections:
                p1, p2 = self.people[i], self.people[j]
                if (infected in (p1, p2)) and (p1.infected != p2.infected):
                    exists = any(i.p1 in (p1,p2) and i.p2 in (p1,p2) for i in self.interactions)
                    if not exists:
                        self.interactions.append(Interaction(p1, p2))
        
        # Update active interaction lines
        # First clear existing
        for line in self.active_interaction_lines:
            line.parent = None
        self.active_interaction_lines = []
        
        # Create new ones
        for interaction in active_interactions:
            line = scene.Line(pos=np.array([[interaction.p1.base_x, interaction.p1.base_y],
                                          [interaction.p2.base_x, interaction.p2.base_y]]),
                            color=Color('white').rgba,
                            width=2,
                            parent=self.view.scene)
            line.set_gl_state('translucent', depth_test=False)
            self.active_interaction_lines.append(line)
        
        # Update stats text
        infected = sum(1 for p in self.people if p.infected)
        stats = f"Infected: {infected}/{NUM_NODES} | Active Interactions: {len(active_interactions)}"
        self.text.text = stats
        
        self.scene.update()

if __name__ == '__main__':
    sim = COVIDSimulator()
    app.run()