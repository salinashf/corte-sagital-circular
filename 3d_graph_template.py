import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv


def plot_cylinder(ax, center, radius, height, num_points=50, color='red'):
    """
    Plots a cylinder in a 3D Matplotlib axis.

    Parameters:
        ax (matplotlib.axes.Axes): The 3D axis to plot on.
        center (tuple): A tuple (cx, cy, cz) representing the center of the cylinder's base.
        radius (float): The radius of the cylinder.
        height (float): The height of the cylinder.
        num_points (int): Number of points to use for drawing the circle.
    """
    cx, cy, cz = center

    # Generate points for the cylinder surface
    theta = np.linspace(0, 2 * np.pi, num_points)
    z = np.linspace(cz, cz + height, num_points)
    theta_grid, z_grid = np.meshgrid(theta, z)

    x = radius * np.cos(theta_grid) + cx
    y = radius * np.sin(theta_grid) + cy

    # Plot the cylinder surface
    ax.plot_surface(x, y, z_grid, alpha=0.6, color='skyblue')

    # Plot the top and bottom circles
    x_circle_bottom = radius * np.cos(theta) + cx
    y_circle_bottom = radius * np.sin(theta) + cy
    z_circle_bottom = np.full_like(theta, cz)
    ax.plot(x_circle_bottom, y_circle_bottom, z_circle_bottom, color=color)

    x_circle_top = radius * np.cos(theta) + cx
    y_circle_top = radius * np.sin(theta) + cy
    z_circle_top = np.full_like(theta, cz + height)
    ax.plot(x_circle_top, y_circle_top, z_circle_top, color=color)


def plot_line_template(ax, center, radio, angulo, directriz):

    # Point Center
    cx, cy, cz = center
    p_center = np.array([cx, cy])
    height_directriz = 0
    B = np.array([radio, 0])

    # Rotación
    radianes = np.deg2rad(angulo)
    rotacion = np.array([
        [np.cos(radianes), -np.sin(radianes)],
        [np.sin(radianes),  np.cos(radianes)]
    ])
    vector = B - p_center
    vector_rotado = rotacion.dot(vector)
    B_rotado = p_center + vector_rotado

    # Punto final de la línea vertical
    P_final = np.array([B_rotado[0], B_rotado[1], directriz])

    # Dibujar líneas
    # Radio
    # ax.plot([p_center[0], B[0]], [p_center[1], B[1]], [0, 0],  color='blue')

    # Draw guideline
    ax.plot([B_rotado[0], B_rotado[0]], [B_rotado[1], B_rotado[1]], [height_directriz, directriz],  color='green')


    # Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
radio = 26
px_cilinder = 0
py_cilinder = 0
# pz_cilinder = 0


# ----------------------------------
# Define template parameters
cylinder_radius = radio
cylinder_center = (px_cilinder, py_cilinder, 0)
# ----------------------------
# ----------------------------
default_csv_name = "outFiles/plantilla_corte_boca_pez.csv"
max_value = 0.0
with open(default_csv_name, 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)  # Skip header row
    for row in csv_reader:
        if len(row) == 3:
            angle_grades, axis_x, axis_y = row
            if int(angle_grades) < 360:
                max_value = max(float(axis_y), max_value)
                plot_line_template(ax,
                                   cylinder_center,
                                   cylinder_radius,
                                   int(angle_grades),
                                   axis_y
                                   )
        else:
            print(f"Skipping row with incorrect number of columns: {row}")


max_value = max_value
# ----------------------------------
# Define cylinder parameters
cylinder_center = (px_cilinder, py_cilinder, -(max_value))
cylinder_height = max_value

# Plot the cylinder
plot_cylinder(ax, cylinder_center, cylinder_radius, cylinder_height, color='blue')

# ----------------------------
# Define cylinder parameters
cylinder_center = (px_cilinder, py_cilinder, max_value)
cylinder_height = max_value

# Plot the cylinder
plot_cylinder(ax, cylinder_center, cylinder_radius, cylinder_height, color='green')

# Set labels and title
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_zlabel('Z-axis')
ax.set_title(f'Cylinder Centered at {cylinder_center}')

# Set equal aspect ratio for better visualization
ax.set_box_aspect([np.ptp(a) for a in [ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()]])

plt.show()
