from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Proceso 
from .forms import FirmaContratoForm
from django.http import Http404
from .services.pdf_services import generar_pdf_firmado

def candidato_view(request, token):
    try:
        proceso = get_object_or_404(Proceso, token=token)
    except Http404:
        return render(request, 'error_enlace.html', {
            'mensaje': 'El enlace al que intentas acceder no es válido.'
        })

    # verificar expiración
    if proceso.ha_expirado():
        if proceso.estado != Proceso.Estado.EXPIRADO:
            proceso.estado = Proceso.Estado.EXPIRADO
            proceso.save()
        return render(request, 'error_enlace.html', {
            'mensaje': 'El enlace ha expirado (48 horas). Contacte a RR.HH.'
        })

    # verificar si ya fue usado
    if proceso.estado == Proceso.Estado.USADO or proceso.usado:
        return render(request, 'error_enlace.html', {
            'mensaje': 'El contrato ya fue firmado y el enlace es de uso único.'
        })

    if request.method == "POST":
        form = FirmaContratoForm(request.POST, request.FILES)

        if form.is_valid():
            firma_img = form.cleaned_data["firma_img"]
            generar_pdf_firmado(proceso, firma_img)

            # marrcar estado del proceso como usado
            proceso.usado = True
            proceso.estado = Proceso.Estado.USADO
            proceso.acceso_link = timezone.now()
            proceso.save()

            # confirmacion de éxito
            return render(request, "confirmacion.html", {"proceso": proceso})
    else:
        form = FirmaContratoForm()

    return render(request, "candidato.html", {"proceso": proceso, "form": form})
