import numpy as np
import matplotlib.pyplot as plt
import csv
import argparse


class CylinderPlotter:
    def __init__(self, radio, px=0, py=0, csv_file="outFiles/plantilla_corte_boca_pez.csv"):
        self.radio = radio
        self.px = px
        self.py = py
        self.csv_file = csv_file
        self.max_value = 0.0
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

    def plot_cylinder(self, center, radius, height, num_points=50, color='red'):
        cx, cy, cz = center
        theta = np.linspace(0, 2 * np.pi, num_points)
        z = np.linspace(cz, cz + height, num_points)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x = radius * np.cos(theta_grid) + cx
        y = radius * np.sin(theta_grid) + cy
        self.ax.plot_surface(x, y, z_grid, alpha=0.6, color='skyblue')

        # Circle outlines
        for offset in [0, height]:
            z_circle = np.full_like(theta, cz + offset)
            x_circle = radius * np.cos(theta) + cx
            y_circle = radius * np.sin(theta) + cy
            self.ax.plot(x_circle, y_circle, z_circle, color=color)

    def plot_line_template(self, center, radio, angulo, directriz):
        cx, cy, _ = center
        p_center = np.array([cx, cy])
        B = np.array([radio, 0])
        radianes = np.deg2rad(angulo)
        rotacion = np.array([[np.cos(radianes), -np.sin(radianes)],
                             [np.sin(radianes),  np.cos(radianes)]])
        vector = B - p_center
        B_rotado = p_center + rotacion.dot(vector)
        self.ax.plot([B_rotado[0]] * 2, [B_rotado[1]] * 2, [0, float(directriz)], color='green')

    def process_csv_and_plot(self):
        center = (self.px, self.py, 0)
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) == 3:
                    angle, _, y_val = row
                    angle = int(angle)
                    if angle < 360:
                        self.max_value = max(float(y_val), self.max_value)
                        self.plot_line_template(center, self.radio, angle, y_val)

    def plot_scene(self):
        self.process_csv_and_plot()
        for direction in [-1, 1]:
            center = (self.px, self.py, direction * self.max_value)
            self.plot_cylinder(center, self.radio, self.max_value, color='blue' if direction < 0 else 'green')

        self.ax.set_xlabel('Eje X')
        self.ax.set_ylabel('Eje Y')
        self.ax.set_zlabel('Eje Z')
        self.ax.set_title(f'Cilindro centrado en  ({self.px}, {self.py}, ±{self.max_value})')
        self.ax.set_box_aspect([np.ptp(a) for a in [self.ax.get_xlim3d(), self.ax.get_ylim3d(), self.ax.get_zlim3d()]])
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Procesar parámetros de dibujo. todo los datos en mm")
    parser.add_argument("-di", "--diametro_injerto", type=float, required=True, help="Diámetro del injerto en mm")
    args = parser.parse_args()
    plotter = CylinderPlotter(radio=(args.diametro_injerto/2))
    plotter.plot_scene()


# Ejecución
if __name__ == "__main__":
    main()
