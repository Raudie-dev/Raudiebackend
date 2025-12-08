from django.shortcuts import render, get_object_or_404
from .models import Prueba, Servicios, Proyecto, Categoria

# Create your views here.
def index(request):
    # Obtener parámetros de búsqueda y filtro
    busqueda = request.GET.get('busqueda', '').strip()
    socio = request.GET.get('socio', '')

    pruebas = Prueba.objects.all()

    if busqueda:
        pruebas = pruebas.filter(nombre__icontains=busqueda)
    if socio in ['si', 'no']:
        pruebas = pruebas.filter(socio=(socio == 'si'))

    # Obtener servicios recientes para mostrar en tarjetas (últimos 6)
    servicios = Servicios.objects.all().order_by('-id')[:6]

    # NUEVO: obtener últimos 4 proyectos
    proyectos = Proyecto.objects.all().order_by('-fecha', '-id')[:4]

    return render(request, 'index.html', {
        'pruebas': pruebas,
        'busqueda': busqueda,
        'socio': socio,
        'servicios': servicios,
        'proyectos': proyectos,  # agregado
    })

# Nueva vista: detalle de un servicio
def servicios_detalle(request, servicio_id):
    servicio = get_object_or_404(Servicios, id=servicio_id)
    return render(request, 'servicio_detalle.html', {'servicio': servicio})

# Nueva vista: listado de proyectos con modal por proyecto
def proyectos(request):
    proyectos = Proyecto.objects.all().order_by('-fecha', '-id')
    categorias = Categoria.objects.all()
    return render(request, 'proyectos.html', {'proyectos': proyectos, 'categorias': categorias})

# Vista estática tipo "linktree" con enlaces fijos
def enlaces(request):

    return render(request, 'enlaces.html')
