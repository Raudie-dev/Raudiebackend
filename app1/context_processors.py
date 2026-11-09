from .models import Servicios, Proyecto, Noticia, Contacto

def servicios_menu(request):
    """Context processor that exposes services, panel user, and landing stats to all templates."""
    servicios = Servicios.objects.all().order_by('nombre')
    
    # Check if an admin is logged in via session
    panel_user = None
    uid = request.session.get('user_admin_id')
    if uid:
        try:
            from app2.models import User_admin
            panel_user = User_admin.objects.get(id=uid)
        except Exception:
            panel_user = None

    total_contactos = Contacto.objects.count()

    return {
        'servicios_menu': servicios,
        'panel_user': panel_user,
        'total_contactos_count': total_contactos,
        'total_servicios_count': servicios.count(),
        'total_proyectos_count': Proyecto.objects.count(),
        'total_noticias_count': Noticia.objects.count(),
    }
