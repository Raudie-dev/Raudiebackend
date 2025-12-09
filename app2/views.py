from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.files.storage import default_storage
import uuid, os
from .models import User_admin
from app1.models import Categoria, Tecnologia
from .crud import (
    crear_servicio, obtener_servicios, eliminar_servicio, actualizar_servicio,
    crear_proyecto, obtener_proyectos, eliminar_proyecto, actualizar_proyecto
)


def login(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        password = request.POST.get('password', '')

        try:
            user = User_admin.objects.get(nombre=nombre)
            if user.bloqueado:
                messages.error(request, 'Usuario bloqueado')
            elif user.password == password or check_password(password, user.password):
                request.session['user_admin_id'] = user.id
                return redirect('control_servicios')
            else:
                messages.error(request, 'Contraseña incorrecta')
            return render(request, 'login.html')
        except User_admin.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return render(request, 'login.html')

    return render(request, 'login.html')


def control_servicios(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')
    try:
        user = User_admin.objects.get(id=user_id)
    except User_admin.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')

    # CRUD Servicios - crear
    if request.method == 'POST' and 'crear_servicio' in request.POST:
        nombre = request.POST.get('nombre', '').strip()
        titulo = request.POST.get('titulo', '').strip()
        precio = request.POST.get('precio', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        caracteristicas_txt = request.POST.get('caracteristicas', '').strip()
        foto = request.FILES.get('foto')

        if not nombre or not precio:
            messages.error(request, 'Nombre y precio son obligatorios')
        else:
            try:
                precio_val = float(precio)
                caracteristicas = [c.strip() for c in caracteristicas_txt.split(',') if c.strip()]
                crear_servicio(nombre, titulo, precio_val, descripcion, caracteristicas, foto)
                messages.success(request, 'Servicio creado correctamente')
                return redirect('control_servicios')
            except ValueError:
                messages.error(request, 'Precio inválido')

    # editar servicio
    if request.method == 'POST' and 'editar_servicio' in request.POST:
        servicio_id = request.POST.get('editar_servicio_id')
        nombre = request.POST.get('nombre', '').strip()
        titulo = request.POST.get('titulo', '').strip()
        precio = request.POST.get('precio', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        caracteristicas_txt = request.POST.get('caracteristicas', '').strip()
        foto = request.FILES.get('foto')

        if not servicio_id:
            messages.error(request, 'ID de servicio faltante')
        else:
            try:
                precio_val = float(precio) if precio else None
                caracteristicas = [c.strip() for c in caracteristicas_txt.split(',') if c.strip()] if caracteristicas_txt != '' else None
                actualizar_servicio(servicio_id, nombre=nombre or None, titulo=titulo or None, precio=precio_val, descripcion=descripcion or None, caracteristicas=caracteristicas, foto=foto)
                messages.success(request, 'Servicio actualizado correctamente')
                return redirect('control_servicios')
            except ValueError:
                messages.error(request, 'Precio inválido')

    # eliminar servicio
    if request.method == 'POST' and 'eliminar_servicio' in request.POST:
        servicio_id = request.POST.get('eliminar_servicio')
        if servicio_id:
            eliminar_servicio(servicio_id)
            messages.success(request, 'Servicio eliminado')

    servicios = obtener_servicios()
    return render(request, 'control_servicios.html', {'servicios': servicios})

# NUEVA/ACTUALIZADA: control_proyectos con manejo de categorias/tecnologias
def control_proyectos(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')
    try:
        user = User_admin.objects.get(id=user_id)
    except User_admin.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')

    categorias = Categoria.objects.all()
    tecnologias = Tecnologia.objects.all()

    # --- Nuevo: crear categoría desde modal ---
    if request.method == 'POST' and 'crear_categoria' in request.POST:
        nombre = request.POST.get('categoria_nombre', '').strip()
        if not nombre:
            messages.error(request, 'El nombre de la categoría es obligatorio')
        else:
            obj, created = Categoria.objects.get_or_create(nombre=nombre)
            if created:
                messages.success(request, f'Categoría "{nombre}" creada')
            else:
                messages.info(request, f'Categoría "{nombre}" ya existe')
            return redirect('control_proyectos')

    # --- Nuevo: crear tecnología desde modal ---
    if request.method == 'POST' and 'crear_tecnologia' in request.POST:
        nombre = request.POST.get('tecnologia_nombre', '').strip()
        if not nombre:
            messages.error(request, 'El nombre de la tecnología es obligatorio')
        else:
            obj, created = Tecnologia.objects.get_or_create(nombre=nombre)
            if created:
                messages.success(request, f'Tecnología "{nombre}" creada')
            else:
                messages.info(request, f'Tecnología "{nombre}" ya existe')
            return redirect('control_proyectos')

    # Crear proyecto
    if request.method == 'POST' and 'crear_proyecto' in request.POST:
        titulo = request.POST.get('titulo', '').strip()
        cliente = request.POST.get('cliente', '').strip()
        fecha = request.POST.get('fecha', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        caracteristicas_txt = request.POST.get('caracteristicas', '').strip()
        archivos = request.FILES.getlist('fotos')
        categoria_ids = request.POST.getlist('categoria_ids')
        tecnologia_ids = request.POST.getlist('tecnologia_ids')

        if not titulo or not fecha:
            messages.error(request, 'Título y fecha son obligatorios')
        else:
            from datetime import datetime
            try:
                fecha_val = datetime.strptime(fecha, '%Y-%m-%d').date()
                caracteristicas = [c.strip() for c in caracteristicas_txt.split(',') if c.strip()]
                fotos_urls = []
                for f in archivos:
                    ext = os.path.splitext(f.name)[1]
                    name = f"proyectos/{uuid.uuid4().hex}{ext}"
                    saved_path = default_storage.save(name, f)
                    try:
                        url = default_storage.url(saved_path)
                    except Exception:
                        url = settings.MEDIA_URL + saved_path
                    fotos_urls.append(url)
                # pasar listas de ids (pueden ser strings) al CRUD
                crear_proyecto(titulo, cliente, fecha_val, descripcion, caracteristicas, fotos_urls, categoria_ids=categoria_ids, tecnologia_ids=tecnologia_ids)
                messages.success(request, 'Proyecto creado correctamente')
                return redirect('control_proyectos')
            except ValueError:
                messages.error(request, 'Fecha inválida, use AAAA-MM-DD')

    # Editar proyecto
    if request.method == 'POST' and 'editar_proyecto' in request.POST:
        proyecto_id = request.POST.get('editar_proyecto_id')
        titulo = request.POST.get('titulo', '').strip()
        cliente = request.POST.get('cliente', '').strip()
        fecha = request.POST.get('fecha', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        caracteristicas_txt = request.POST.get('caracteristicas', '').strip()
        archivos = request.FILES.getlist('fotos')  # si se suben, reemplazan fotos
        categoria_ids = request.POST.getlist('categoria_ids')
        tecnologia_ids = request.POST.getlist('tecnologia_ids')

        if not proyecto_id:
            messages.error(request, 'ID de proyecto faltante')
        else:
            from datetime import datetime
            try:
                fecha_val = datetime.strptime(fecha, '%Y-%m-%d').date() if fecha else None
                caracteristicas = [c.strip() for c in caracteristicas_txt.split(',') if c.strip()] if caracteristicas_txt != '' else None
                fotos_urls = None
                if archivos:
                    fotos_urls = []
                    for f in archivos:
                        ext = os.path.splitext(f.name)[1]
                        name = f"proyectos/{uuid.uuid4().hex}{ext}"
                        saved_path = default_storage.save(name, f)
                        try:
                            url = default_storage.url(saved_path)
                        except Exception:
                            url = settings.MEDIA_URL + saved_path
                        fotos_urls.append(url)
                actualizar_proyecto(proyecto_id, titulo= titulo or None, cliente=cliente or None, fecha=fecha_val, descripcion=descripcion or None, caracteristicas=caracteristicas, fotos=fotos_urls, categoria_ids=categoria_ids if categoria_ids != [] else None, tecnologia_ids=tecnologia_ids if tecnologia_ids != [] else None)
                messages.success(request, 'Proyecto actualizado correctamente')
                return redirect('control_proyectos')
            except ValueError:
                messages.error(request, 'Fecha inválida, use AAAA-MM-DD')

    # Eliminar proyecto
    if request.method == 'POST' and 'eliminar_proyecto' in request.POST:
        proyecto_id = request.POST.get('eliminar_proyecto')
        if proyecto_id:
            eliminar_proyecto(proyecto_id)
            messages.success(request, 'Proyecto eliminado')

    proyectos = obtener_proyectos()
    return render(request, 'control_proyectos.html', {'proyectos': proyectos, 'categorias': categorias, 'tecnologias': tecnologias})