import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

import matplotlib.pyplot as plt
import ezdxf


def dxf_to_pdf(dxf_filepath, pdf_filepath):
    try:
        doc = ezdxf.readfile(dxf_filepath)
        msp = doc.modelspace()

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc)
        ctx.set_current_layout(msp)
        ctx.current_layout.set_colors(bg='#FFFFFF')
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp, finalize=True)

        fig.savefig(pdf_filepath, dpi=300)  # Adjust DPI as needed
        plt.close(fig)
        print(f"Successfully converted {dxf_filepath} to {pdf_filepath}")

    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
    except ezdxf.error.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")


# Example usage:
dxf_to_pdf(r"T:\boca-de-pez\plantilla_corte_boca_pez.dxf", r"T:\boca-de-pez\output.pdf")
