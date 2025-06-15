import ezdxf
from matplotlib import patches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import tkinter as tk
from tkinter import filedialog


class DXFVisualizer:
    def __init__(self, frame_content_visor):
        self.frame_content_visor = frame_content_visor
        self.current_canvas = None
        self.ax = None
        self.figure = None
        self.entities_bbox = None

    def plot_line(self, ax, start, end):
        ax.plot([start[0], end[0]], [start[1], end[1]], color='k')

    def plot_circle(self, ax, center, radius):
        circle = plt.Circle(center, radius, fill=False, color='k')
        ax.add_artist(circle)

    def translate_entities(self, entities):
        min_x = float('inf')
        min_y = float('inf')

        for entity in entities:
            if entity.dxftype() == 'LINE':
                min_x = min(min_x, entity.dxf.start[0], entity.dxf.end[0])
                min_y = min(min_y, entity.dxf.start[1], entity.dxf.end[1])
            elif entity.dxftype() == 'CIRCLE':
                min_x = min(min_x, entity.dxf.center[0] - entity.dxf.radius)
                min_y = min(min_y, entity.dxf.center[1] - entity.dxf.radius)
            elif entity.dxftype() == 'LWPOLYLINE':
                for vertex in entity.get_points('xy'):
                    min_x = min(min_x, vertex[0])
                    min_y = min(min_y, vertex[1])

        for entity in entities:
            if entity.dxftype() == 'LINE':
                entity.dxf.start = (entity.dxf.start[0] - min_x, entity.dxf.start[1] - min_y)
                entity.dxf.end = (entity.dxf.end[0] - min_x, entity.dxf.end[1] - min_y)
            elif entity.dxftype() == 'CIRCLE':
                entity.dxf.center = (entity.dxf.center[0] - min_x, entity.dxf.center[1] - min_y)
            elif entity.dxftype() == 'LWPOLYLINE':
                new_vertices = [(v[0] - min_x, v[1] - min_y) for v in entity.get_points('xy')]
                entity.set_points(new_vertices)

    def draw(self, dxf_file):
        if not dxf_file:
            return
        if self.current_canvas:
            self.current_canvas.get_tk_widget().pack_forget()

        doc = ezdxf.readfile(dxf_file)
        msp = doc.modelspace()
        self.translate_entities(msp)
        fig, ax = plt.subplots()

        for entity in msp:
            if entity.dxftype() == 'LINE':
                self.plot_line(ax, entity.dxf.start, entity.dxf.end)
            elif entity.dxftype() == 'CIRCLE':
                self.plot_circle(ax, entity.dxf.center, entity.dxf.radius)
            elif entity.dxftype() == 'LWPOLYLINE':
                vertices = entity.get_points('xy')
                for i in range(len(vertices)):
                    self.plot_line(ax, vertices[i - 1], vertices[i])

        ax.set_aspect('equal')
        plt.title('DXF Viewer')
        mplcursors.cursor(hover=True)

        self.current_canvas = FigureCanvasTkAgg(fig, master=self.frame_content_visor)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def apply_zoom(self, zoom_percent):
        pass


class CrearGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Plantilla de Visualización corte")
        self.root.geometry("800x600")
        self.root.configure(bg="white")
        self.visualizador = None

    def crear_header(self):
        tk.Label(self.root, text="Corte sagital", bg="lightblue", fg="white",
                 font=("Arial", 16), height=2).pack(side="top", fill="x")

    def crear_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill="both", expand=True)

    def crear_menu(self):
        nav_frame = tk.Frame(self.main_frame, width=120, bg="#f0f0f0")
        nav_frame.pack(side="left", fill="y")

        tk.Button(nav_frame, text="Abrir archivo DXF", fg="blue", anchor="w",
                  command=self.open_file).pack(fill="x", padx=10, pady=5)

        tk.Button(nav_frame, text="Cerrar", fg="blue", anchor="w",
                  command=self.root.quit).pack(fill="x", padx=10, pady=5)

        zoom_scale = tk.Scale(nav_frame, from_=50, to=200, orient='horizontal',
                              label="Zoom (%)", command=self.aplicar_zoom)
        zoom_scale.set(100)
        zoom_scale.pack(fill="x", pady=(10, 0))

    def crear_visor(self):
        self.frame_content_visor = tk.Frame(self.main_frame, bg="white")
        self.frame_content_visor.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(self.frame_content_visor, text="Plantilla", font=("Arial", 14, "bold")).pack(anchor="w")
        tk.Label(self.frame_content_visor, text="Plantilla del corte sagital",
                 font=("Arial", 12)).pack(anchor="w", pady=(5, 0))

        self.canvas_frame = tk.Frame(self.frame_content_visor, bg="white")
        self.canvas_frame.pack(fill="both", expand=True)

        self.visualizador = DXFVisualizer(self.canvas_frame)

    def crear_footer(self):
        tk.Label(self.root, text="Salinas Henry", bg="lightblue", fg="white", height=2).pack(side="bottom", fill="x")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DXF Files", "*.dxf")])
        if file_path:
            self.visualizador.draw(file_path)

    def aplicar_zoom(self, valor):
        if self.visualizador:
            self.visualizador.apply_zoom(int(valor))

    def show(self):
        self.crear_header()
        self.crear_main_frame()
        self.crear_menu()
        self.crear_visor()
        self.crear_footer()
        self.root.mainloop()


if __name__ == '__main__':
    CrearGUI().show()
