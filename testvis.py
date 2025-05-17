import numpy as np
from vispy import scene, app
from vispy.scene import visuals

# Create canvas and view
canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='black')
view = canvas.central_widget.add_view()
view.camera = scene.cameras.PanZoomCamera(aspect=1)
view.camera.set_range()

# Generate 100,000 random 2D points
n = 100_000
positions = np.random.uniform(-1, 1, (n, 2))  # X, Y positions
sizes = np.full(n, 5)  # Constant size for all circles
colors = np.ones((n, 4))  # RGBA (white)
colors[:, 3] = 0.8  # Slight transparency

# Create markers visual (each point is a small circle)
scatter = visuals.Markers()
scatter.set_data(positions, face_color=colors, size=sizes, edge_width=0)

# Add to scene
view.add(scatter)

# Run the app
if __name__ == '__main__':
    app.run()
