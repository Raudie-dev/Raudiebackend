from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import Prueba, Servicios, Proyecto, Categoria, Noticia
from .services_data import get_servicios, get_servicio_by_id, get_servicio_by_slug, get_otros_servicios
from django.utils.text import slugify
from django.http import Http404

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

    # Obtener servicios oficiales definidos en código (no modificables desde el panel)
    servicios = get_servicios()

    # Obtener últimos 6 proyectos y categorías
    proyectos = Proyecto.objects.all().order_by('-fecha', '-id')[:6]
    categorias = Categoria.objects.all()

    # Obtener últimas noticias (3 para el grid editorial del index)
    noticias = Noticia.objects.all().order_by('-fecha', '-id')[:3]

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
        'categorias': categorias,
        'noticias': noticias,
        'mensaje_bienvenida': mensaje_bienvenida,
    })

# Vista: detalle de un servicio por slug (sin mostrar ID en la URL)
def servicios_detalle(request, servicio_ref):
    ref_str = str(servicio_ref).strip()
    servicio = None

    if ref_str.isdigit():
        servicio = get_servicio_by_id(int(ref_str))
        if servicio and servicio.get('slug'):
            return redirect('servicio_detalle', servicio_ref=servicio['slug'])
        try:
            db_serv = Servicios.objects.get(id=int(ref_str))
            return redirect('servicio_detalle', servicio_ref=slugify(db_serv.nombre))
        except (Servicios.DoesNotExist, ValueError):
            return redirect('index')

    servicio = get_servicio_by_slug(ref_str)
    if not servicio:
        for s in get_servicios():
            if slugify(s.get('nombre', '')) == ref_str:
                servicio = s
                break
    if not servicio:
        for db_s in Servicios.objects.all():
            if slugify(db_s.nombre) == ref_str:
                servicio = db_s
                break
    if not servicio:
        return redirect('index')

    serv_id = servicio['id'] if isinstance(servicio, dict) else servicio.id
    otros_servicios = get_otros_servicios(serv_id)
    return render(request, 'servicio_detalle.html', {
        'servicio': servicio,
        'otros_servicios': otros_servicios,
    })

# Vista: detalle de un proyecto por slug (sin mostrar ID en la URL)
def proyecto_detalle(request, proyecto_ref):
    ref_str = str(proyecto_ref).strip()
    proyecto = None

    if ref_str.isdigit():
        proyecto = get_object_or_404(Proyecto, pk=int(ref_str))
        if slugify(proyecto.titulo):
            return redirect('proyecto_detalle', proyecto_ref=slugify(proyecto.titulo))
    else:
        for p in Proyecto.objects.all().order_by('-fecha', '-id'):
            if slugify(p.titulo) == ref_str:
                proyecto = p
                break
        if not proyecto and ref_str.startswith('proyecto-'):
            tail_id = ref_str.replace('proyecto-', '')
            if tail_id.isdigit():
                proyecto = Proyecto.objects.filter(pk=int(tail_id)).first()
        if not proyecto:
            raise Http404('Proyecto no encontrado')

    proyectos_relacionados = Proyecto.objects.exclude(pk=proyecto.pk).order_by('-fecha', '-id')[:3]
    return render(request, 'proyecto_detalle.html', {
        'proyecto': proyecto,
        'proyectos_relacionados': proyectos_relacionados
    })

def proyectos(request):
    proyectos = Proyecto.objects.all().order_by('-fecha', '-id')
    categorias = Categoria.objects.all()
    return render(request, 'proyectos.html', {'proyectos': proyectos, 'categorias': categorias})

# Nueva vista: listado de noticias e insights
def noticias(request):
    categoria_filtro = request.GET.get('categoria', '').strip()
    noticias_qs = Noticia.objects.all().order_by('-fecha', '-id')
    if categoria_filtro:
        noticias_qs = noticias_qs.filter(categoria__iexact=categoria_filtro)

    categorias = [c for c in Noticia.objects.values_list('categoria', flat=True).distinct() if c]

    return render(request, 'noticias.html', {
        'noticias': noticias_qs,
        'categorias': categorias,
        'categoria_filtro': categoria_filtro,
    })

# Vista: lectura completa del artículo de noticia por slug (sin mostrar ID en la URL)
def noticia_detalle(request, noticia_ref):
    ref_str = str(noticia_ref).strip()
    noticia = None

    if ref_str.isdigit():
        noticia = get_object_or_404(Noticia, pk=int(ref_str))
        if (noticia.slug or slugify(noticia.titulo)):
            return redirect('noticia_detalle', noticia_ref=(noticia.slug or slugify(noticia.titulo)))
    else:
        noticia = Noticia.objects.filter(slug=ref_str).first()
        if not noticia:
            for n in Noticia.objects.all():
                if n.slug == ref_str or slugify(n.titulo) == ref_str:
                    noticia = n
                    break
        if not noticia:
            raise Http404('Noticia no encontrada')

    noticias_relacionadas = Noticia.objects.exclude(pk=noticia.pk).order_by('-fecha', '-id')[:3]
    return render(request, 'noticia_detalle.html', {
        'noticia': noticia,
        'noticias_relacionadas': noticias_relacionadas,
    })

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
