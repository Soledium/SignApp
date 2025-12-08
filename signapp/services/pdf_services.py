
import hashlib
from io import BytesIO

import fitz  # PyMuPDF
from PIL import Image
from django.core.files.base import ContentFile


def generar_pdf_firmado(proceso, firma_file):
    """
    Toma el PDF base de la plantilla del proceso, estampa la firma
    en la primera página y guarda el PDF final en proceso.pdf_firmado.
    Devuelve el hash SHA256 del PDF final.
    """

    # 1) Abrir el PDF base (plantilla elegida por RR.HH.)
    plantilla_path = proceso.plantilla.archivo.path
    doc = fitz.open(plantilla_path)

    # 2) Abrir la imagen de la firma con Pillow
    firma_image = Image.open(firma_file)

    # Convertir la firma a PNG en memoria
    firma_bytes_io = BytesIO()
    firma_image.save(firma_bytes_io, format="PNG")
    firma_bytes = firma_bytes_io.getvalue()

    # 3) Insertar la firma en la primera página
    page = doc[0]                       # primera página
    page_rect = page.rect               # tamaño de la página

    # Tamaño de la firma: 30% del ancho de la página
    firma_width = page_rect.width * 0.3
    ratio = firma_image.height / firma_image.width
    firma_height = firma_width * ratio

    # Posición: abajo a la derecha con un margen
    margin_x = page_rect.width * 0.1
    margin_y = page_rect.height * 0.1

    x1 = page_rect.width - firma_width - margin_x
    y1 = page_rect.height - firma_height - margin_y
    x2 = x1 + firma_width
    y2 = y1 + firma_height

    rect = fitz.Rect(x1, y1, x2, y2)
    page.insert_image(rect, stream=firma_bytes)

    # 4) Guardar el PDF resultante en memoria
    output_buffer = BytesIO()
    doc.save(output_buffer)
    doc.close()

    pdf_bytes = output_buffer.getvalue()

    # 5) Calcular hash de integridad
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

    # 6) Guardar el PDF en el FileField del proceso (sin guardar aún el modelo)
    django_file = ContentFile(pdf_bytes)
    filename = f"contrato_firmado_{proceso.id or 'tmp'}.pdf"
    proceso.pdf_firmado.save(filename, django_file, save=False)
    proceso.pdf_hash = pdf_hash

    return pdf_hash
