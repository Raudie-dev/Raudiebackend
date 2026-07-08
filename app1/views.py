from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
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

    # Manejo de formulario de contacto (envía correo a la cuenta admin)
    if request.method == 'POST' and 'contact_message' in request.POST:
        contact_name = request.POST.get('contact_name', '').strip()
        contact_email = request.POST.get('contact_email', '').strip()
        contact_message = request.POST.get('contact_message', '').strip()

        if not contact_message:
            messages.error(request, 'El mensaje es obligatorio')
        else:
            subject = f'Contacto web: {contact_name or "(sin nombre)"}'
            body = f'Nombre: {contact_name}\nEmail: {contact_email}\n\nMensaje:\n{contact_message}'
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, ['raudie.dev@gmail.com'], fail_silently=False)
                messages.success(request, 'Mensaje enviado correctamente. Gracias por contactarnos.')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Error enviando correo: {e}')

    from app2.models import ConfigBot
    bot = ConfigBot.objects.first()
    mensaje_bienvenida = bot.mensaje_bienvenida if (bot and bot.mensaje_bienvenida) else '¡Hola! ¿En qué te puedo ayudar hoy?'

    return render(request, 'index.html', {
        'pruebas': pruebas,
        'busqueda': busqueda,
        'socio': socio,
        'servicios': servicios,
        'proyectos': proyectos,
        'mensaje_bienvenida': mensaje_bienvenida,
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

from django.http import JsonResponse
import json
from .models import Contacto

def guardar_contacto(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('name', '')
            whatsapp = request.POST.get('phone', '')
            email = request.POST.get('email', '')
            mensaje = request.POST.get('message', '')
            
            contacto = Contacto.objects.create(
                nombre=nombre,
                whatsapp=whatsapp,
                email=email,
                mensaje=mensaje
            )
            return JsonResponse({'success': True, 'message': 'Guardado exitosamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
