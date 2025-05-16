import pygame
import sys
import math

# Initialize Pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Create a world surface (same size as our screen - can't zoom out beyond this)
world_width, world_height = screen_width, screen_height
world_surface = pygame.Surface((world_width, world_height))

# Fill the world with some content (for visualization)
world_surface.fill((50, 50, 50))
for i in range(10):
    pygame.draw.circle(world_surface, 
                     (i*25, i*25, 255-i*25), 
                     (i*80, i*60), 
                     30)

# Camera variables
camera_offset = [0, 0]  # Current camera position
target_offset = [0, 0]   # Target camera position
zoom_factor = 1.0        # Current zoom level (1.0 = normal view)
target_zoom = 1.0        # Target zoom level
transition_speed = 0.05  # Speed of smooth transition
min_zoom = 1.0           # Can't zoom out beyond initial view
max_zoom = 4.0           # Maximum zoom in level

# Button properties
button_rect = pygame.Rect(10, 50, 200, 40)  # x, y, width, height
button_color = (70, 130, 180)  # Steel blue
button_hover_color = (100, 150, 200)
button_text = "Go to (400,300)"
button_font = pygame.font.SysFont(None, 24)
target_world_position = (400, 300)  # Hard-coded coordinates to zoom to
target_zoom_level = 2.0             # Zoom level when button is clicked

def ease_out_quad(x):
    """Easing function for smooth animation"""
    return 1 - (1 - x) * (1 - x)

def start_transition_to_target():
    """Start smooth transition to target position"""
    global target_offset, target_zoom
    
    # Set target zoom (clamped to allowed range)
    target_zoom = max(min_zoom, min(target_zoom_level, max_zoom))
    
    # Calculate the required camera offset to center the target
    target_offset[0] = target_world_position[0] - (screen_width/2) / target_zoom
    target_offset[1] = target_world_position[1] - (screen_height/2) / target_zoom
    
    # Ensure we don't view outside the world
    target_offset[0] = max(0, min(world_width - screen_width/target_zoom, target_offset[0]))
    target_offset[1] = max(0, min(world_height - screen_height/target_zoom, target_offset[1]))

def update_camera():
    """Smoothly update camera position and zoom"""
    global camera_offset, zoom_factor
    
    # Smooth interpolation with easing
    interp = ease_out_quad(transition_speed)
    
    # Update camera position
    camera_offset[0] += (target_offset[0] - camera_offset[0]) * interp
    camera_offset[1] += (target_offset[1] - camera_offset[1]) * interp
    
    # Update zoom factor
    zoom_factor += (target_zoom - zoom_factor) * interp
    
    # Ensure we don't view outside the world
    camera_offset[0] = max(0, min(world_width - screen_width/zoom_factor, camera_offset[0]))
    camera_offset[1] = max(0, min(world_height - screen_height/zoom_factor, camera_offset[1]))

def draw_button():
    """Draw the button with hover effect"""
    mouse_pos = pygame.mouse.get_pos()
    color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
    
    pygame.draw.rect(screen, color, button_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2, border_radius=5)  # Border
    
    text_surf = button_font.render(button_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if button_rect.collidepoint(event.pos):
                    start_transition_to_target()
        
        elif event.type == pygame.MOUSEWHEEL:
            # For wheel zoom, we'll interrupt any current transition
            mouse_pos = pygame.mouse.get_pos()
            
            # Calculate world position under mouse
            world_x = mouse_pos[0] / zoom_factor + camera_offset[0]
            world_y = mouse_pos[1] / zoom_factor + camera_offset[1]
            
            # Determine zoom direction (can't zoom out beyond min_zoom)
            if event.y > 0:  # Zoom in
                target_zoom = min(max_zoom, zoom_factor + 0.1)
            else:  # Zoom out
                target_zoom = max(min_zoom, zoom_factor - 0.1)
            
            # Update target offset to keep mouse position stable
            target_offset[0] = world_x - mouse_pos[0] / target_zoom
            target_offset[1] = world_y - mouse_pos[1] / target_zoom
            
            # Ensure we don't view outside the world
            target_offset[0] = max(0, min(world_width - screen_width/target_zoom, target_offset[0]))
            target_offset[1] = max(0, min(world_height - screen_height/target_zoom, target_offset[1]))
    
    # Update camera position smoothly
    update_camera()
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Draw the world surface (scaled if zoomed in)
    if zoom_factor > 1.0:
        # Calculate the visible area of the world
        visible_width = screen_width / zoom_factor
        visible_height = screen_height / zoom_factor
        visible_area = pygame.Rect(
            camera_offset[0],
            camera_offset[1],
            visible_width,
            visible_height
        )
        
        # Draw the appropriate portion of the world surface
        subsurf = world_surface.subsurface(visible_area)
        scaled_surf = pygame.transform.scale(subsurf, (screen_width, screen_height))
        screen.blit(scaled_surf, (0, 0))
    else:
        # At 1.0 zoom or less, just draw the whole surface
        screen.blit(world_surface, (0, 0))
    
    # Draw the button (on top of everything)
    draw_button()
    
    # Display debug info
    font = pygame.font.SysFont(None, 24)
    debug_text = [
        f"Zoom: {zoom_factor:.1f}x (target: {target_zoom:.1f})",
        f"Camera: ({camera_offset[0]:.1f}, {camera_offset[1]:.1f})",
        f"Min Zoom: {min_zoom}x (can't zoom out further)"
    ]
    
    for i, text in enumerate(debug_text):
        text_surf = font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 100 + i * 25))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()