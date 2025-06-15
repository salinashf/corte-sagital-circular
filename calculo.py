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
default_bg_color = "#2DAB33"  # White
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
    print(f"Perímetro plantilla: {perimetro_plantilla} mm")

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

    # Calcular límites verticales
    y_max = max(y_values)
    y_base = min(y_values)
    y_range = y_max - y_base
    y_min = y_base - y_range  # Extiende el margen inferior
    y_dim_line = y_base - y_range / 2  # Línea de cota

    print(f"y_min: {y_base}")
    print(f"y_max: {y_max}")

    # Coordenadas horizontales
    x_start, x_end = x_values[0], x_values[-1]
    y_start, y_end = y_values[0], y_values[-1]

    # Dibuja marco superior
    msp.add_line((x_start, y_max), (x_end, y_max))  # horizontal superior
    msp.add_line((x_start, y_start), (x_end, y_end))  # horizontal inferior
    msp.add_line((x_start, y_start), (x_start, y_max))  # vertical izquierda
    msp.add_line((x_end, y_end), (x_end, y_max))  # vertical derecha

    # Dibuja marco inferior
    msp.add_line((x_start, y_min), (x_end, y_min))  # horizontal inferior
    msp.add_line((x_start, y_start), (x_start, y_min))  # vertical izquierda
    msp.add_line((x_end, y_end), (x_end, y_min), dxfattribs={"linetype": "DASHED"})  # vertical derecha entrecortada

    # Agrega una cota lineal horizontal
    dim = msp.add_linear_dim(
        base=(0, y_dim_line),  # posición de la línea de cota
        p1=(x_start, y_min),
        p2=(x_end, y_min),
        text="<> mm",
        override={"dimcolor": 40, "dimtxt": 1.0, "dimjust": 0}  # opcional: personaliza estilo
    )
    dim.render()  # ¡Importante! Esto genera la geometría visible
    # Agrega una cota lineal vertial total
    dim = msp.add_linear_dim(
        base=(x_start + y_range*3, 0),
        p1=(x_start, y_max),
        p2=(x_start, y_min),
        angle=-90,
        text="<> mm",
        override={"dimjust": 4}
    )
    dim.set_arrows(blk=ezdxf.ARROWS.closed_filled, size=1.5)
    dim.render()
    # Agrega una cota lineal vertial superior
    dim = msp.add_linear_dim(
        base=(x_start + y_range*1, 0),
        p1=(x_start, y_start),
        p2=(x_start, y_max),
        angle=90,
        text="<> mm"

    )
    dim.set_arrows(blk=ezdxf.ARROWS.closed_filled, size=1.5)
    dim.render()
    # Agrega una cota lineal vertial inferior
    dim = msp.add_linear_dim(
        base=(x_start + y_range*2, 0),
        p1=(x_start, y_start),
        p2=(x_start, y_min),
        angle=-90,
        text="<> mm",
        override={"dimjust": 4}

    )
    dim.set_arrows(blk=ezdxf.ARROWS.closed_filled, size=1.5)
    dim.render()

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
