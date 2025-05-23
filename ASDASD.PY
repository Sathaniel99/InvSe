from django.shortcuts import render
from .models import Objeto

def aux(request):
    queryset = Objeto.objects.all()

    # Obtener valores del GET
    opcion1 = request.GET.get('opcion1')
    opcion2 = request.GET.get('opcion2')
    opcion3 = request.GET.get('opcion3')
    opcion4 = request.GET.get('opcion4')

    # Aplicar filtros solo si los valores no están vacíos
    if opcion1:
        queryset = queryset.filter(opcion1=opcion1)
    if opcion2:
        queryset = queryset.filter(opcion2=opcion2)
    if opcion3:
        queryset = queryset.filter(opcion3=opcion3)
    if opcion4:
        queryset = queryset.filter(opcion4=opcion4)

    return render(request, 'template.html', {'resultados': queryset})