import pygame
import random
import math
import sys

# Initialize Pygameimport numpy as np
from vispy import app, gloo, scene
from vispy.scene import visuals
import pickle
import math
import random
import time

# Constants
WIDTH, HEIGHT = 1000, 800
BASE_RADIUS = 8
INFECTION_PROB = 0.7
INTERACTION_TIME = 2.0
APPROACH_SPEED = 0.5
BG_COLOR = (0.08, 0.08, 0.08, 1.0)

# Load data
with open("adjList.pickle", "rb") as f:
    people = pickle.load(f)

with open("pos.pickle", "rb") as f:
    pos = pickle.load(f)

NUM_NODES = len(people)

# Visualization Canvas
canvas = scene.SceneCanvas(keys='interactive', size=(WIDTH, HEIGHT), bgcolor=BG_COLOR, show=True)
view = canvas.central_widget.add_view()
view.camera = scene.cameras.PanZoomCamera(aspect=1)
view.camera.set_range(x=(0, WIDTH), y=(0, HEIGHT))

# Markers for people
person_scatter = scene.visuals.Markers(parent=view.scene)
colors = np.array([[0, 1, 0, 1] for _ in range(NUM_NODES)])  # Green initially

# Setup positions
positions = np.array([[p.x, p.y] for p in people])

# Draw lines
connections = people  # reuse your original connections structure
connection_lines = []
for i, j in connections:
    connection_lines.append(pos[i])
    connection_lines.append(pos[j])
connection_lines = np.array(connection_lines)
connection_visual = scene.visuals.Line(pos=connection_lines, color=(0.5, 0.5, 0.5, 1), method='gl', parent=view.scene)

# Infect patient zero
patient_zero = random.choice(people)
patient_zero.infected = True
colors[patient_zero.id] = [1, 0, 0, 1]  # Red

person_scatter.set_data(pos=positions, face_color=colors, size=BASE_RADIUS*2)

# Update function
def update(event):
    global positions, colors

    # You can simulate infection spread here...
    # For now, just rotate colors for demo
    for p in people:
        if p.infected:
            colors[p.id] = [1, 0, 0, 1]
        else:
            colors[p.id] = [0, 1, 0, 1]

    person_scatter.set_data(pos=positions, face_color=colors, size=BASE_RADIUS*2)

timer = app.Timer(interval=1/60, connect=update, start=True)

if __name__ == '__main__':
    app.run()

pygame.init()

# Screen setup
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COVID-19 Spread Simulator")
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BG = (20, 20, 20)

# Simulation parameters
NUM_NODES = 25
BASE_RADIUS = 8
INFECTION_PROB = 0.7  # 70% transmission chance
INTERACTION_TIME = 2.0  # seconds
APPROACH_SPEED = 0.5  # movement speed
MIN_DISTANCE = 50  # minimum space between nodes

class Person:
    def __init__(self, x, y, id):
        self.id = id
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.radius = BASE_RADIUS
        self.infected = False
        self.color = GREEN
        self.pulse_phase = 0
        self.pulse_size = 0
        
    def update(self, dt):
        # Handle pulsing animation
        if self.pulse_size > 0:
            self.pulse_phase += dt * 10
            self.radius = BASE_RADIUS + math.sin(self.pulse_phase) * self.pulse_size
            self.pulse_size = max(0, self.pulse_size - dt * 2)
        else:
            self.radius = BASE_RADIUS
            
    def start_pulse(self):
        self.pulse_size = 5
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class Interaction:
    def __init__(self, person1, person2):
        self.p1 = person1
        self.p2 = person2
        self.progress = 0  # 0-1 for approach, 1-0 for retreat
        self.phase = "approach"  # approach, interact, retreat
        self.time_elapsed = 0
        self.completed = False
        
    def update(self, dt):
        if self.phase == "approach":
            self.progress = min(1, self.progress + APPROACH_SPEED * dt)
            
            # Move along line toward midpoint
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
                # Determine infection
                if (self.p1.infected and not self.p2.infected and 
                    random.random() < INFECTION_PROB):
                    self.p2.infected = True
                    self.p2.color = RED
                elif (self.p2.infected and not self.p1.infected and 
                      random.random() < INFECTION_PROB):
                    self.p1.infected = True
                    self.p1.color = RED
                    
        elif self.phase == "retreat":
            self.progress = max(0, self.progress - APPROACH_SPEED * dt)
            
            # Move back to original positions
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
                
    def draw_connection(self, surface):
        pygame.draw.line(surface, GRAY, 
                        (self.p1.base_x, self.p1.base_y),
                        (self.p2.base_x, self.p2.base_y), 1)

# Create people with minimum spacing
people = []
for i in range(NUM_NODES):
    while True:
        x = random.randint(50, WIDTH-50)
        y = random.randint(50, HEIGHT-50)
        
        # Check spacing
        valid = True
        for p in people:
            if math.dist((x, y), (p.x, p.y)) < MIN_DISTANCE:
                valid = False
                break
                
        if valid:
            people.append(Person(x, y, i))
            break

# Create connections between people
connections = []
for i in range(NUM_NODES):
    for j in range(i+1, NUM_NODES):
        if random.random() < 0.1:  # Connection probability
            connections.append((i, j))

# Infect random patient zero
patient_zero = random.choice(people)
patient_zero.infected = True
patient_zero.color = RED

# Create initial interactions
interactions = []
for i, j in connections:
    if people[i].infected or people[j].infected:
        p1, p2 = people[i], people[j]
        if p1.infected != p2.infected:  # Only between infected and healthy
            interactions.append(Interaction(p1, p2))

def draw_dotted_line(surf, color, start, end, width=1, dash_length=5):
    dx, dy = end[0]-start[0], end[1]-start[1]
    dist = math.hypot(dx, dy)
    dx /= dist
    dy /= dist
    
    for i in range(0, int(dist), dash_length*2):
        s = (start[0]+dx*i, start[1]+dy*i)
        e = (start[0]+dx*(i+dash_length), start[1]+dy*(i+dash_length))
        pygame.draw.line(surf, color, s, e, width)

# Main game loop
running = True
last_time = pygame.time.get_ticks()
while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0  # Delta time in seconds
    last_time = current_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update all people
    for person in people:
        person.update(dt)
    
    # Update interactions
    active_interactions = []
    new_infections = []
    
    for interaction in interactions[:]:
        interaction.update(dt)
        
        if not interaction.completed:
            active_interactions.append(interaction)
        else:
            interactions.remove(interaction)
            
            # Check if new infections occurred
            if interaction.p1.infected and interaction.p1.color == RED:
                new_infections.append(interaction.p1)
            if interaction.p2.infected and interaction.p2.color == RED:
                new_infections.append(interaction.p2)
    
    # Create new interactions for newly infected
    for infected in new_infections:
        for i, j in connections:
            p1, p2 = people[i], people[j]
            if (infected in (p1, p2) and 
                p1.infected != p2.infected and 
                not any(i.p1 in (p1,p2) and i.p2 in (p1,p2) for i in interactions)):
                interactions.append(Interaction(p1, p2))
    
    # Draw everything
    screen.fill(BG)
    
    # Draw all connections
    for i, j in connections:
        p1, p2 = people[i], people[j]
        draw_dotted_line(screen, GRAY, (p1.base_x, p1.base_y), (p2.base_x, p2.base_y))
    
    # Draw active interaction connections
    for interaction in active_interactions:
        pygame.draw.line(screen, WHITE, 
                        (interaction.p1.base_x, interaction.p1.base_y),
                        (interaction.p2.base_x, interaction.p2.base_y), 2)
    
    # Draw people
    for person in people:
        person.draw(screen)
    
    # Display stats
    font = pygame.font.SysFont('Arial', 24)
    infected = sum(1 for p in people if p.infected)
    stats = f"Infected: {infected}/{NUM_NODES} | Active Interactions: {len(active_interactions)}"
    text = font.render(stats, True, WHITE)
    screen.blit(text, (20, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()