from django.shortcuts import render, get_object_or_404
from .models import Proceso 
from .forms import FirmaContratoForm
from django.http import Http404


def candidato_view(request, token):
    try:
        proceso = get_object_or_404(Proceso, token=token)
    except Http404:
        return render(request, 'error_enlace.html', {'mensaje': 'Enlace inválido o inexistente.'})
    if proceso.ha_expirado:
        if proceso.estado != Proceso.Estado.EXPIRADO:
            proceso.estado = Proceso.Estado.EXPIRADO
            proceso.save()
            
        return render(request, 'error_enlace.html', {'mensaje': 'El enlace ha expirado (48 horas). Contacte a RR.HH.'})
    
    if proceso.estado == Proceso.Estado.USADO:
        return render(request, 'error_enlace.html', {'mensaje': 'El contrato ya fue firmado y el enlace es de uso único.'})

    form = FirmaContratoForm() 
    return render(request, "candidato.html", {'proceso': proceso, 'form': form})