from .models import Servicios

def servicios_menu(request):
    """Context processor that exposes services to all templates for the navbar."""
    servicios = Servicios.objects.all().order_by('nombre')
    return {'servicios_menu': servicios}
