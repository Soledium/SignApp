from django.shortcuts import render


def candidato_view(request):
    return render(request, "candidato.html")
    