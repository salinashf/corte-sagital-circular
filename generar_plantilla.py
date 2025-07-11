from pathlib import Path
import time
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import math
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import pymupdf, layout
from ezdxf.math import global_bspline_interpolation
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import (
    Configuration,
    BackgroundPolicy,
    ColorPolicy,
    LineweightPolicy,
)
import svgwrite
import csv
# Todos los cálculos y funciones necesarios para el cálculo de coordenadas del corte sagital
# Los datos se generaran en un formato json  que se pueda utilizar para graficar
# Todas la unidades están en mm
# Parámetros
diametro_base = 87  # 8.7cm
diametro_injerto = 52  # 5.2cm
numero_divisiones = 120
lineweight = 1.5  # mm
angulo_inclinacion = 90
grosor_injerto = 1

#  Rutas de los archivos de salida
default_dxf_name = "outFiles/plantilla_corte_boca_pez.dxf"
default_svg_name = "outFiles/plantilla_corte_boca_pez.svg"
default_csv_name = "outFiles/plantilla_corte_boca_pez.csv"
default_img_name = "outFiles/plantilla_corte_boca_pez.png"
default_pdf_name = "outFiles/plantilla_corte_boca_pez.pdf"
# Formato Permitido
''' 
	layout.PageAlignment.TOP_LEFT 
	layout.PageAlignment.TOP_CENTER 
	layout.PageAlignment.TOP_RIGHT 
	layout.PageAlignment.MIDDLE_LEFT 
	layout.PageAlignment.MIDDLE_CENTER 
	layout.PageAlignment.MIDDLE_RIGHT 
	layout.PageAlignment.BOTTOM_LEFT 
	layout.PageAlignment.BOTTOM_CENTER 
	layout.PageAlignment.BOTTOM_RIGHT 
'''
page_alignment = layout.PageAlignment.TOP_LEFT
# default_pdf_name_escala = "outFiles/plantilla_corte_boca_pez_escala.pdf"
# default_pdf_name_simple = "outFiles/plantilla_corte_boca_pez_simple.pdf"

# Margen para la plantilla
# en caso de imprimir en  a4 o otro papel  es para la figura no quede
# al  borde del limite de la impresora
x_margen = 20
y_margen = 150
# header del csv
header_csv = ['angle_grades', 'axis_x_mm', 'axis_y_mm']

# Parámetros por defecto para la conversión a imagen
default_dpi = 300
default_bg_color = "#2DAB33"  # White

# Función para calcular las coordenadas del corte sagital , boca de pez


def calcular_directrices_45(radio_base, radio_injerto, angulo_directriz, angulo_inclinacion):
    # angulo de la directriz y de inclinacion  pasado a  radianes, por motivos de que libreria math lo requiere
    adr = math.radians(angulo_directriz)
    air = math.radians(angulo_inclinacion)

    calcul_directriz = (radio_injerto + math.cos(adr) * radio_injerto) * math.tan(air) + \
        (radio_base - math.sqrt(
            radio_base**2 - (math.sin(adr) * radio_injerto)**2
        )
    ) \
        / math.cos(air)
    return calcul_directriz


def calcular_directrices_90(radio_base, radio_injerto, angulo_directriz, angulo_inclinacion):
    # angulo de la directriz pasado a  radianes, por motivos de que libreria math lo requiere
    adr = math.radians(angulo_directriz)
    calcul_directriz = radio_base - \
        math.sqrt(radio_base**2 - (math.sin(adr) * radio_injerto)**2)
    return calcul_directriz


# def calcular_directrices_90(radio_base, radio_injerto, angulo_directriz):
#     adr = math.radians(angulo_directriz)

#     rst_cal = math.sin(adr) * radio_injerto
#     rst_cal = math.sqrt(math.pow(radio_base, 2) - math.pow(rst_cal, 2))
#     rst_cal = radio_base - rst_cal
#     return rst_cal


def coordenadas_corte_sagital():

    # Cálculos
    radio_base = diametro_base / 2
    radio_injerto = (diametro_injerto - grosor_injerto) / 2
    perimetro_plantilla = diametro_injerto * math.pi
    segmento_plantilla = perimetro_plantilla / numero_divisiones
    angulo_division = 360 / numero_divisiones
    print(f"Perímetro plantilla: {perimetro_plantilla} mm")

    # Calcular puntos
    lista_puntos = []
    puntos = []
    data_plantilla = []
    for seqno, angulo_paso in enumerate(range(0, 361, int(angulo_division))):
        rst = 0.0
        if angulo_inclinacion == 90:
            rst = calcular_directrices_90(radio_base, radio_injerto, angulo_paso, angulo_inclinacion)
        else:
            rst = calcular_directrices_45(radio_base, radio_injerto, angulo_paso, angulo_inclinacion)

        x = seqno * segmento_plantilla
        y = rst
        puntos.append((x, y))
        lista_puntos.append({"x": x, "y": y})
        data_plantilla.append([angulo_paso, x, y])
    # Extraer valores
    x_values = [p["x"] for p in lista_puntos]
    y_values = [p["y"] for p in lista_puntos]
    return x_values, y_values, puntos, data_plantilla

# agrega un margen a los puntos


def incremente_margen(x_values, y_values, puntos):
    x_values_add = [x_p + x_margen for x_p in x_values]
    y_values_add = [y_p + y_margen for y_p in y_values]
    punto_add = [(x_p + x_margen, y_p + y_margen) for x_p, y_p in puntos]
    return x_values_add, y_values_add, punto_add


def obtener_max_min_ejes(puntos):
    """Devuelve los valores máximos y mínimos de X e Y en una lista de puntos."""
    if not puntos:
        return None, None, None, None

    x_min, y_min = puntos[0]
    x_max, y_max = puntos[0]

    for x, y in puntos:
        x_min = min(x_min, x)
        x_max = max(x_max, x)
        y_min = min(y_min, y)
        y_max = max(y_max, y)

    return x_max, y_max, x_min, y_min


def generar_CSV(datos_plantilla):
    csv_file_path = default_csv_name  # Asegúrate de que esta ruta sea válida

    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header_csv)
            csv_writer.writerows(datos_plantilla)
        print(f"Archivo CSV sobrescrito exitosamente en: {csv_file_path}")
    except PermissionError:
        print(f"❌ No se puede sobrescribir el archivo. Asegúrate de que no esté abierto: {csv_file_path}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")


def generar_svg(x_values, y_values, puntos, ):
    # Dimensiones del papel A4 en mm
    width_mm = 210
    height_mm = 297

    # Crear el documento SVG con tamaño basado en mm
    dwg = svgwrite.Drawing(default_svg_name, size=(
        f"{width_mm}mm", f"{height_mm}mm"), viewBox=f"0 0 {width_mm} {height_mm}")

    x_max, y_max, x_base, y_base = obtener_max_min_ejes(puntos)
    y_range = abs(y_max - y_base)
    print(x_max, y_max, x_base, y_base)
    linea_punteada = "5,3"
    # linea base
    dwg.add(dwg.line(start=puntos[0], end=puntos[-1], stroke="black", stroke_width=0.3,
                     stroke_dasharray=linea_punteada))
    dwg.add(dwg.line(start=(x_base, (y_base-y_range)), end=(x_max, y_max-y_range*2),
            stroke="black", stroke_width=0.3, stroke_dasharray=linea_punteada))
    dwg.add(dwg.line(start=(x_base, (y_base+y_range)), end=(x_max, y_base+y_range),
            stroke="black", stroke_width=0.3, stroke_dasharray=linea_punteada))
    dwg.add(dwg.line(start=(x_base, (y_base-y_range)), end=(x_base, (y_base+y_range)),
            stroke="black", stroke_width=0.3,  stroke_dasharray=linea_punteada))

    dwg.add(dwg.line(start=(x_max, y_base+y_range), end=(x_max, (y_base-y_range)),
            stroke="black", stroke_width=0.3, stroke_dasharray=linea_punteada))

    # Agregar los puntos individuales en milímetros
    for x, y in puntos:
        dwg.add(dwg.circle(center=(x, y), r=0.5, fill="red"))
        dwg.add(dwg.line(start=(x, y_base), end=(x, y), stroke="black", stroke_width=0.3))
        dwg.add(dwg.circle(center=(x, y_base), r=0.5, fill="green"))

    # Agregar la polilínea conectando los puntos en milímetros
    dwg.add(dwg.polyline(points=puntos, stroke="blue", fill="none", stroke_width=0.3))

    # Guardar el archivo SVG
    dwg.save()
    print(f"Archivo SVG guardado como... '{default_svg_name}'.")


def generar_dxf(x_values, y_values, puntos):

    doc = ezdxf.new("R2010")
    # para hoja a4 210 x 297
    # Create an A4 page layout
    # doc.header["$LIMMIN"] = (0, 0)
    # doc.header["$LIMMAX"] = (210, 297)
    # page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
    # layout = doc.layouts.create("A4_Portrait", fmt=PaperFormat.A4, landscape=False)

    doc.units = ezdxf.units.MM  # Establecer unidad en milímetros
    msp = doc.modelspace()
    auditor = doc.audit()

    # Calcular límites verticales
    y_max = max(y_values)
    y_base = min(y_values)
    lineweight_conver = lineweight * 100

    y_range = y_max - y_base
    y_min = y_base - y_range  # Extiende el margen inferior
    y_dim_line = y_base - y_range / 2  # Línea de cota

    # Coordenadas horizontales
    x_start, x_end = x_values[0], x_values[-1]
    y_start, y_end = y_values[0], y_values[-1]
    # Espieza a dibujar
    for x, y in zip(x_values, y_values):
        msp.add_point((x, y))
        msp.add_line((x, y_base), (x, y))

    # Dibuja marco superior
    msp.add_line((x_start, y_max), (x_end, y_max), dxfattribs={"lineweight": lineweight_conver})  # horizontal superior
    msp.add_line((x_start, y_start), (x_end, y_end), dxfattribs={
                 "lineweight": lineweight_conver})  # horizontal inferior
    msp.add_line((x_start, y_start), (x_start, y_max), dxfattribs={
                 "lineweight": lineweight_conver})  # vertical izquierda
    msp.add_line((x_end, y_end), (x_end, y_max), dxfattribs={"lineweight": lineweight_conver})  # vertical derecha

    # Dibuja marco inferior
    msp.add_line((x_start, y_min), (x_end, y_min), dxfattribs={"lineweight": lineweight_conver})  # horizontal inferior
    msp.add_line((x_start, y_start), (x_start, y_min), dxfattribs={
                 "lineweight": lineweight_conver})  # vertical izquierda
    msp.add_line((x_end, y_end), (x_end, y_min), dxfattribs={
                 "linetype": "DASHED", "lineweight": lineweight_conver})  # vertical derecha entrecortada

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
    # crea la linae uniendo todos los puntos
    msp.add_lwpolyline(puntos, dxfattribs={"closed": False, "lineweight": lineweight_conver})
    # Crear archivo DFX
    # Guardar el archivo DXF
    doc.saveas(default_dxf_name)
    print(f"Archivo DXF guardado como... {default_dxf_name}")

    # # Crear un PDF para imprimir
    # backend = pymupdf.PyMuPdfBackend()
    # Frontend(RenderContext(doc), backend).draw_layout(msp)
    # pdf_bytes = backend.get_pdf_bytes(layout.Page(100, 40, layout.Units.mm))
    # Path(default_pdf_name_simple).write_bytes(pdf_bytes)
    # print(f"PDF simple guardado como... {default_pdf_name_simple}")

    # backend_B = pymupdf.PyMuPdfBackend()
    # Frontend(RenderContext(doc), backend_B).draw_layout(msp)
    # pdf_bytes_B = backend_B.get_pdf_bytes(layout.Page(0, 0, layout.Units.mm), settings=layout.Settings(scale=10))
    # Path(default_pdf_name_escala).write_bytes(pdf_bytes_B)
    # print(f"PDF con img  en escala  guardada como... {default_pdf_name_escala}")

    config_l = Configuration(
        background_policy=BackgroundPolicy.WHITE,
        custom_bg_color="#002082",
        color_policy=ColorPolicy.MONOCHROME_DARK_BG,
        custom_fg_color="#ced8f7",
        lineweight_policy=LineweightPolicy.RELATIVE,
        lineweight_scaling=0.5,
    )
    backend_l = pymupdf.PyMuPdfBackend()
    height, width, _ = layout.PAGE_SIZES["ISO A4"]

    Frontend(RenderContext(doc), backend_l, config=config_l).draw_layout(msp)
    page = layout.Page(width, height, margins=layout.Margins.all(15))
    pdf_bytes = backend_l.get_pdf_bytes(
        page,
        settings=layout.Settings(
            fit_page=False,
            page_alignment=page_alignment,
            scale=1.0)
    )
    Path(default_pdf_name).write_bytes(pdf_bytes)
    print(f"PDF con dxf alineada guardado como... {default_pdf_name}")

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    ctx.set_current_layout(msp)
    ezdxf.addons.drawing.properties.MODEL_SPACE_BG_COLOR = default_bg_color
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    fig.savefig(default_img_name, dpi=default_dpi)
    print(f"Imagen guardada como {default_img_name}")


# Generar coordenadas y exportarlas a DXF
x_values, y_values, puntos, datos_plantilla = coordenadas_corte_sagital()
x_val_m, y_val_m, puntos_m = incremente_margen(x_values, y_values, puntos)
# ---------------------

# generar_dxf_con_linea(puntos, "corte_sagital.dxf")
generar_dxf(x_val_m, y_val_m, puntos_m)
generar_svg(x_val_m, y_val_m, puntos_m)
generar_CSV(datos_plantilla)
