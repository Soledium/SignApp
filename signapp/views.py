from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Proceso 
from .forms import FirmaContratoForm
from django.http import Http404


def candidato_view(request, token):
    # Buscar proceso por token
    try:
        proceso = get_object_or_404(Proceso, token=token)
    except Http404:
        return render(
            request,
            'error_enlace.html',
            {'mensaje': 'Enlace inválido o inexistente.'}
        )

    # Validar expiración
    if proceso.ha_expirado():
        if proceso.estado != Proceso.Estado.EXPIRADO:
            proceso.estado = Proceso.Estado.EXPIRADO
            proceso.save()
            
        return render(request,'error_enlace.html',{'mensaje': 'El enlace ha expirado (48 horas). Contacte a RR.HH.'})
    
    # Validar si ya fue usado
    if proceso.estado == Proceso.Estado.USADO or proceso.usado:
        return render(request,'error_enlace.html',{'mensaje': 'El contrato ya fue firmado y el enlace es de uso único.'})

    # Procesar formulario
    if request.method == "POST":
        form = FirmaContratoForm(request.POST, request.FILES)

        if form.is_valid():
            firma_img = form.cleaned_data["firma_img"]
            consentimiento = form.cleaned_data["consentimiento"]

            # Aquí iría la lógica real de generación del PDF final:
            #   - abrir plantilla: proceso.plantilla.archivo.path
            #   - estampar la firma (firma_img)
            #   - guardar resultado en contratos/firmados/
            #
            # Ejemplo "fake" por ahora:
            # pdf_path = PDFService.generar_pdf_firmado(
            #     plantilla_path=proceso.plantilla.archivo.path,
            #     firma_file=firma_img,
            #     proceso=proceso,
            # )
            #
            # proceso.pdf_firmado.name = pdf_path

            # Marcar proceso como usado
            proceso.usado = True
            proceso.estado = Proceso.Estado.USADO
            proceso.acceso_link = timezone.now()
            proceso.save()

            return render(
                request,"candidato_ok.html",{"proceso": proceso})
    else:
        form = FirmaContratoForm()

    # GET (form vacío)
    return render(
        request,"candidato.html",{'proceso': proceso,'form': form}
    )
