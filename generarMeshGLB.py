import json
import trimesh
import numpy as np
import json
import numpy as np
import trimesh

default_json_name = "outFiles/plantilla_corte_boca_pez.json"
default_glb_name = "outFiles/plantilla_corte_boca_pez.glb"
# Cargar el archivo JSON
with open(default_json_name, "r", encoding="utf-8") as f:
    data = json.load(f)

radio = data["radio"]
puntos = data["puntos"]

# Parámetros del cilindro hueco
grosor_cilindro = 1
altura = radio*2
radio_interior = radio - grosor_cilindro
if radio_interior <= 0:
    raise ValueError("⚠️ El grosor es demasiado grande. El radio interior sería negativo.")

segments = [
    [[a["x"], a["y"], a["z"]], [b["x"], b["y"], b["z"]]]
    for punto in puntos
    for a, b in [(punto["3D"]["pt_a"], punto["3D"]["pt_b"])]
]

# Crear líneas 3D
lineas_path = trimesh.load_path(np.array(segments))

# Crear cilindros (exterior e interior) y alinearlos
traslacion_z = [0, 0, -altura / 2]
cil_ext = trimesh.creation.cylinder(radius=radio, height=altura)
cil_ext.apply_translation(traslacion_z)

cil_int = trimesh.creation.cylinder(radius=radio_interior, height=altura)
cil_int.apply_translation(traslacion_z)

# Crear cilindro hueco con diferencia booleana
try:
    cil_hueco = cil_ext.difference(cil_int)
except Exception as e:
    raise RuntimeError(f"❌ Error creando el cilindro hueco: {e}")

cil_hueco.visual.face_colors = [180, 180, 255, 255]

# Armar escena y exportar
scene = trimesh.Scene([lineas_path, cil_hueco])
scene.export(default_glb_name)
scene.show()

print(f"✅ Exportación completa:  {default_glb_name}")
