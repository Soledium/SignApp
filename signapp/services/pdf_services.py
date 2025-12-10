
import hashlib
from io import BytesIO

import fitz  
from PIL import Image
from django.core.files.base import ContentFile


def quitar_fondo(imagen):
    """
    Quita el fondo tomando como referencia el color de la esquina superior izquierda.
    Todo píxel que se parezca a ese color se vuelve transparente.
    Funciona mejor para papel cuadriculado / beige.
    """

    imagen = imagen.convert("RGBA")
    datos = list(imagen.getdata())
    fondo_r, fondo_g, fondo_b, fondo_a = datos[0]

    UMBRAL = 50

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

    plantilla_path = proceso.plantilla.archivo.path
    doc = fitz.open(plantilla_path)

    firma_image = Image.open(firma_file)
    firma_image = quitar_fondo(firma_image)

    firma_bytes_io = BytesIO()
    firma_image.save(firma_bytes_io, format="PNG")
    firma_bytes = firma_bytes_io.getvalue()

    pagina = proceso.plantilla.pagina_firma
    total_pages = len(doc)

    page_index = min(max(pagina - 1, 0), total_pages - 1)
    page = doc[page_index]
    page_rect = page.rect

    ancho_rel = proceso.plantilla.firma_ancho_rel or 0.3
    firma_width = page_rect.width * ancho_rel

    ratio = firma_image.height / firma_image.width
    firma_height = firma_width * ratio

    x1 = (page_rect.width - firma_width) / 2
    y1 = page_rect.height - firma_height - 50  

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

