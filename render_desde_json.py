import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

default_json_name = "outFiles/plantilla_corte_boca_pez.json"

# Cargar el archivo JSON
with open(default_json_name, "r", encoding="utf-8") as f:
    data = json.load(f)

radio = data["radio"]
puntos = data["puntos"]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Graficar cada línea 3D
for punto in puntos:
    p3d = punto["3D"]
    a = p3d["pt_a"]
    b = p3d["pt_b"]

    x_vals = [a["x"], b["x"]]
    y_vals = [a["y"], b["y"]]
    z_vals = [a["z"], b["z"]]

    # Línea entre pt_a y pt_b
    ax.plot(x_vals, y_vals, z_vals, color='green', linewidth=1)

    # Marcar pt_a (base) en rojo
    ax.scatter(a["x"], a["y"], a["z"], color='red', marker='o', label='Base' if punto["angulo"] == 0 else "")

    # Marcar pt_b (altura) en azul
    ax.scatter(b["x"], b["y"], b["z"], color='blue', marker='x', label='Altura' if punto["angulo"] == 0 else "")

# Etiquetas y estilo
ax.set_xlabel("Eje X")
ax.set_ylabel("Eje Y")
ax.set_zlabel("Eje Z")
ax.set_title("Líneas 3D desde JSON")

# Evitar entradas repetidas en la leyenda
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys())

plt.tight_layout()
plt.show()
