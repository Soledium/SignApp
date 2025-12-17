import hashlib
from io import BytesIO

import fitz
from PIL import Image
from django.core.files.base import ContentFile


def quitar_fondo(imagen):

    imagen = imagen.convert("RGBA")
    datos = list(imagen.getdata())
    fondo_r, fondo_g, fondo_b, fondo_a = datos[0]

    UMBRAL = 60

    nuevo = []
    for pixel in datos:
        r, g, b, a = pixel
        if (
            abs(r - fondo_r) < UMBRAL and
            abs(g - fondo_g) < UMBRAL and
            abs(b - fondo_b) < UMBRAL
        ):
            nuevo.append((255, 255, 255, 0))
        else:
            nuevo.append((r, g, b, 255))

    imagen.putdata(nuevo)
    return imagen


def generar_pdf_firmado(proceso, firma_file):
    base_path = None
    pagina = 1
    ancho_rel = 0.3

    if hasattr(proceso, "pdf_empresa") and proceso.pdf_empresa:
        base_path = proceso.pdf_empresa.path
        pagina = getattr(proceso, "pagina_firma", 1) or 1
        ancho_rel = getattr(proceso, "firma_ancho_rel", 0.3) or 0.3
    elif getattr(proceso, "plantilla", None) and proceso.plantilla and proceso.plantilla.archivo:
        base_path = proceso.plantilla.archivo.path
        pagina = getattr(proceso.plantilla, "pagina_firma", 1) or 1
        ancho_rel = getattr(proceso.plantilla, "firma_ancho_rel", 0.3) or 0.3
    else:
        raise ValueError("No hay PDF base asociado al proceso (pdf_empresa o plantilla).")

    doc = fitz.open(base_path)

    firma_image = Image.open(firma_file)
    firma_image = quitar_fondo(firma_image)

    firma_bytes_io = BytesIO()
    firma_image.save(firma_bytes_io, format="PNG")
    firma_bytes = firma_bytes_io.getvalue()

    total_pages = len(doc)
    page_index = min(max(pagina - 1, 0), total_pages - 1)
    page = doc[page_index]
    page_rect = page.rect

    firma_width = page_rect.width * ancho_rel
    ratio = firma_image.height / firma_image.width
    firma_height = firma_width * ratio


    if proceso.firma_x_rel is not None and proceso.firma_y_rel is not None:
        x1 = page_rect.width * proceso.firma_x_rel
        y1 = page_rect.height * proceso.firma_y_rel
    else:
        x1 = (page_rect.width - firma_width) / 2
        y1 = page_rect.height - firma_height - 30

    x2 = x1 + firma_width
    y2 = y1 + firma_height

    rect = fitz.Rect(x1, y1, x2, y2)
    page.insert_image(rect, stream=firma_bytes)

    output_buffer = BytesIO()
    doc.save(output_buffer)
    doc.close()

    pdf_bytes = output_buffer.getvalue()
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

    django_file = ContentFile(pdf_bytes)
    filename = f"contrato_firmado_{proceso.id or 'tmp'}.pdf"
    proceso.pdf_firmado.save(filename, django_file, save=False)
    proceso.pdf_hash = pdf_hash

    return pdf_hash
