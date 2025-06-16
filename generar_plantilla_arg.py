import argparse
import math
import os
import ezdxf
import matplotlib.pyplot as plt
from pathlib import Path
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing import pymupdf, layout
from ezdxf.addons.drawing.config import (
    Configuration,
    BackgroundPolicy,
    ColorPolicy,
    LineweightPolicy,
)
import svgwrite


class CorteSagital:
    def __init__(self, diametro_base, diametro_injerto, numero_divisiones, ancho_linea):
        self.diametro_base = diametro_base
        self.diametro_injerto = diametro_injerto
        self.numero_divisiones = numero_divisiones
        self.lineweight = ancho_linea

        # Rutas de los archivos de salida
        self.default_dxf_name = "outFiles/plantilla_corte_boca_pez.dxf"
        self.default_svg_name = "outFiles/plantilla_corte_boca_pez.svg"
        self.default_img_name = "outFiles/plantilla_corte_boca_pez.png"
        self.default_pdf_name = "outFiles/plantilla_corte_boca_pez.pdf"
        self.page_alignment = layout.PageAlignment.TOP_LEFT
        self.default_dpi = 300
        self.default_bg_color = "#2DAB33"
        self.x_margen = 0
        self.y_margen = 0

    def calcular_coordenadas(self):
        radio_base = self.diametro_base / 2
        radio_injerto = self.diametro_injerto / 2
        perimetro_plantilla = self.diametro_injerto * math.pi
        segmento_plantilla = perimetro_plantilla / self.numero_divisiones
        angulo_division = 360 / self.numero_divisiones

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

        x_values = [p["x"] for p in lista_puntos]
        y_values = [p["y"] for p in lista_puntos]
        return x_values, y_values, puntos

    def obtener_max_min_ejes(self, puntos):
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

    def generar_svg(self, x_values, y_values, puntos):

        # Dimensiones del papel A4 en mm
        width_mm = 210
        height_mm = 297

        # Crear el documento SVG con tamaño basado en mm
        dwg = svgwrite.Drawing(self.default_svg_name, size=(
            f"{width_mm}mm", f"{height_mm}mm"), viewBox=f"0 0 {width_mm} {height_mm}")

        x_max, y_max, x_base, y_base = self.obtener_max_min_ejes(puntos)
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
        print(f"Archivo SVG guardado como... '{self.default_svg_name}'.")

    def generar_dxf(self, x_values, y_values, puntos):
        doc = ezdxf.new("R2010")
        doc.units = ezdxf.units.MM
        msp = doc.modelspace()

        # Calcular límites verticales
        y_max = max(y_values)
        y_base = min(y_values)
        lineweight_conver = self.lineweight * 100
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
        msp.add_line((x_start, y_max), (x_end, y_max), dxfattribs={
                     "lineweight": lineweight_conver})  # horizontal superior
        msp.add_line((x_start, y_start), (x_end, y_end), dxfattribs={
            "lineweight": lineweight_conver})  # horizontal inferior
        msp.add_line((x_start, y_start), (x_start, y_max), dxfattribs={
            "lineweight": lineweight_conver})  # vertical izquierda
        msp.add_line((x_end, y_end), (x_end, y_max), dxfattribs={"lineweight": lineweight_conver})  # vertical derecha

        # Dibuja marco inferior
        msp.add_line((x_start, y_min), (x_end, y_min), dxfattribs={
                     "lineweight": lineweight_conver})  # horizontal inferior
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

        doc.saveas(self.default_dxf_name)
        print(f"Archivo DXF guardado como... {self.default_dxf_name}")
        self.__generar_pdf(doc, msp)
        self.__generar_imagen(doc, msp)

    def __generar_pdf(self, doc, msp):
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
            settings=layout.Settings(fit_page=False, page_alignment=self.page_alignment, scale=1.0),
        )
        Path(self.default_pdf_name).write_bytes(pdf_bytes)
        print(f"PDF guardado como... {self.default_pdf_name}")

    def __generar_imagen(self, doc, msp):
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc)
        ctx.set_current_layout(msp)
        ezdxf.addons.drawing.properties.MODEL_SPACE_BG_COLOR = self.default_bg_color
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp, finalize=True)
        fig.savefig(self.default_img_name, dpi=self.default_dpi)
        print(f"Imagen guardada como {self.default_img_name}")


def main():
    parser = argparse.ArgumentParser(description="Procesar parámetros de dibujo. todo los datos en mm")
    parser.add_argument("-db", "--diametro_base", type=float, required=True, help="Diámetro de la base en mm")
    parser.add_argument("-di", "--diametro_injerto", type=float, required=True, help="Diámetro del injerto en mm")
    parser.add_argument("-nd", "--numero_divisiones", type=int, required=True,
                        help="Número de divisiones, o numero de cordenadas")
    parser.add_argument("-al", "--ancho_linea", type=float, required=True, help="Grosor de la del dibujo, línea en mm")

    args = parser.parse_args()

    corte = CorteSagital(args.diametro_base, args.diametro_injerto, args.numero_divisiones, args.ancho_linea)

    x_values, y_values, puntos = corte.calcular_coordenadas()
    corte.generar_dxf(x_values, y_values, puntos)
    corte.generar_svg(x_values, y_values, puntos)


if __name__ == "__main__":
    main()
