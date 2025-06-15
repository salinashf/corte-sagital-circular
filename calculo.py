import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import re
import math
import matplotlib.pyplot as plt
import ezdxf
# Todos los cálculos y funciones necesarios para el cálculo de coordenadas del corte sagital
# Los datos se generaran en un formato json  que se pueda utilizar para graficar
# Todas la unidades están en mm
# Parámetros
diametro_base = 87  # 8.7cm
diametro_injerto = 52  # 5.2cm
numero_divisiones = 120
#  Margen para la plantilla
x_margen = 30
y_margen = 275
nombre_archivo_dxf = "outFiles/plantilla_corte_boca_pez.dxf"
# Parámetros por defecto para la conversión a imagen
default_img_res = 300
default_bg_color = "#2B8A13"  # White
default_img_name = "outFiles/plantilla_corte_boca_pez"
default_img_format = '.png'

# Función para calcular las coordenadas del corte sagital , boca de pez


def coordenadas_corte_sagital():

    # Cálculos
    radio_base = diametro_base / 2
    radio_injerto = diametro_injerto / 2
    perimetro_plantilla = diametro_injerto * math.pi
    segmento_plantilla = perimetro_plantilla / numero_divisiones
    angulo_division = 360 / numero_divisiones

    # Calcular puntos
    lista_puntos = []
    puntos = []
    for seqno, angulo_paso in enumerate(range(0, 361, int(angulo_division))):
        rst = math.sin(math.radians(angulo_paso)) * radio_injerto
        rst = math.sqrt(math.pow(radio_base, 2) - math.pow(rst, 2))
        rst = radio_base - rst
        x = seqno * segmento_plantilla
        y = rst
        puntos.append((x, y))
        lista_puntos.append({"x": x, "y": y})
    # Extraer valores
    x_values = [p["x"] for p in lista_puntos]
    y_values = [p["y"] for p in lista_puntos]
    return x_values, y_values, puntos

# agrega un margen a los puntos


def incremente_margen(x_values, y_values, puntos):
    x_values_add = [x_p + x_margen for x_p in x_values]
    y_values_add = [y_p + y_margen for y_p in y_values]
    punto_add = [(x_p + x_margen, y_p + y_margen) for x_p, y_p in puntos]
    return x_values_add, y_values_add, punto_add


def generar_dxf_con_puntos(x_values, y_values, puntos):

    doc = ezdxf.new()
    doc.units = ezdxf.units.MM  # Establecer unidad en milímetros
    msp = doc.modelspace()
    auditor = doc.audit()
    for x, y in zip(x_values, y_values):
        msp.add_point((x, y))

    y_max = max(y_values)
    print(f"y_max: {y_max}")
    y_base = min(y_values)
    y_slice = (y_max - y_base)
    y_min = y_base - (y_slice)  # 10% debajo del mínimo
    print(f"y_min: {y_base}")
    # Dibuja los margenes de la  plantilla
    # linea horizontal superior plantilla
    msp.add_line((x_values[0], y_max), (x_values[-1], y_max))
    # linea horizontal inferior plantilla
    msp.add_line((x_values[0], y_values[0]), (x_values[-1], y_values[-1]))
    # linea vertical  superior izquierda
    msp.add_line((x_values[0], y_values[0]), (x_values[0], y_max))
    # linea vertical  superior derecha
    msp.add_line((x_values[-1], y_values[-1]), (x_values[-1], y_max))
    # ---------------------------------
    # Dibuja los margenes de la plantilla la parte inferior
    # linea horizontal inferior plantilla
    msp.add_line((x_values[0], y_min), (x_values[-1], y_min))

    # linea vertical  inferior izquierda
    msp.add_line((x_values[0], y_values[0]), (x_values[0], y_min))
    # linea vertical  inferior derecha
    msp.add_line((x_values[-1], y_values[-1]), (x_values[-1], y_min),
                 dxfattribs={"linetype": "DASHED"})

    # Agrega una cota lineal horizontal
    dim = msp.add_linear_dim(
        base=(0, y_base-(y_slice/2)),  # posición de la línea de cota
        p1=(x_values[0], y_min),     # punto inicial
        p2=(x_values[-1], y_min),   # punto final
        text="<> mm",
        override={"dimexe": 1.0, "dimtxt": 2.0, "dimcolor": 40},  # opcional: personaliza estilo
    )

    dim.render()  # ¡Importante! Esto genera la geometría visible

    # Crear una polilínea con los puntos
    msp.add_lwpolyline(puntos, dxfattribs={"closed": False})
    # Guardar el archivo DXF
    doc.saveas(nombre_archivo_dxf)
    print(f"Archivo DXF guardado como {nombre_archivo_dxf}")

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    ctx.set_current_layout(msp)
    ezdxf.addons.drawing.properties.MODEL_SPACE_BG_COLOR = default_bg_color
    # ctx.current_layout.set_colors(bg="#E432B4")
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    first_param = f"{default_img_name}{default_img_format}"
    fig.savefig(first_param, dpi=default_img_res)
    print(f"Imagen guardada como {first_param}")


def generar_dxf_con_linea(puntos, nombre_archivo="corte_sagital.dxf"):
    doc = ezdxf.new()
    doc.units = ezdxf.units.MM  # Asegura que las unidades sean milímetros
    msp = doc.modelspace()

    # Crear una polilínea con los puntos
    msp.add_lwpolyline(puntos, dxfattribs={"closed": False})

    doc.saveas(nombre_archivo)
    print(f"Archivo DXF guardado como {nombre_archivo}")


# Generar coordenadas y exportarlas a DXF
x_values, y_values, puntos = coordenadas_corte_sagital()
x_val_m, y_val_m, puntos_m = incremente_margen(x_values, y_values, puntos)
# ---------------------

# generar_dxf_con_linea(puntos, "corte_sagital.dxf")
generar_dxf_con_puntos(x_val_m, y_val_m, puntos_m)
