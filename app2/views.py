from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from datetime import datetime
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django_ratelimit.decorators import ratelimit
from io import BytesIO
import uuid, os, requests, PyPDF2, docx, re, base64
import json as json_mod
import pandas as pd
from PIL import Image, UnidentifiedImageError
from .models import User_admin, ConfigBot, TelegramMessage, ContextFile, Departamento, Agente, ClienteConsulta, CostItem, ProjectHourlyRate, ProjectCostType, IncomeRecord, ExpenseRecord, PublicacionMarketing
from .crypto import encrypt_value, decrypt_value
from app1.models import Categoria, Tecnologia, Contacto, Proyecto, Noticia, Servicios
from django.db.models import Sum
from .crud import (
    crear_servicio, obtener_servicios, eliminar_servicio, actualizar_servicio,
    crear_proyecto, obtener_proyectos, eliminar_proyecto, actualizar_proyecto
)
from functools import wraps

def admin_permission_required(perm_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = _get_session_user(request)
            if not user:
                messages.error(request, 'Debe iniciar sesión primero')
                return redirect('login')
            # Admin master override
            if user.nombre == 'admin':
                return view_func(request, *args, **kwargs)
            # Check permissions
            user_perms = user.permisos or []
            if perm_name not in user_perms:
                messages.error(request, 'No tienes permiso para acceder a esta sección.')
                # Redirect to their first available permission
                for p in user_perms:
                    if p in ['control_servicios', 'control_proyectos', 'marketing', 'estado', 'conversaciones', 'configuracion', 'telegram_configuracion', 'departamentos', 'agentes', 'contabilidad_costos', 'contabilidad_finanzas', 'generar_cotizacion', 'control_usuarios']:
                        return redirect(p)
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



def save_image_as_webp(uploaded_file, folder):
    webp_name = f"{folder}/{uuid.uuid4().hex}.webp"
    original_ext = os.path.splitext(uploaded_file.name)[1] or '.webp'
    fallback_name = f"{folder}/{uuid.uuid4().hex}{original_ext}"
    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGBA')
        else:
            image = image.convert('RGB')

        buffer = BytesIO()
        image.save(buffer, format='WEBP', quality=80, method=6)
        buffer.seek(0)
        content = ContentFile(buffer.read(), name=webp_name)
        saved_path = default_storage.save(webp_name, content)
        return saved_path
    except (UnidentifiedImageError, OSError):
        uploaded_file.seek(0)
        return default_storage.save(fallback_name, uploaded_file)


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
                if user.nombre == 'admin':
                    return redirect('estado')
                user_perms = user.permisos or []
                for p in ['control_servicios', 'control_proyectos', 'marketing', 'estado', 'conversaciones', 'configuracion', 'telegram_configuracion', 'departamentos', 'agentes', 'contabilidad_costos', 'contabilidad_finanzas', 'generar_cotizacion', 'control_usuarios']:
                    if p in user_perms:
                        return redirect(p)
                return redirect('perfil')
            else:
                messages.error(request, 'Contraseña incorrecta')
            return render(request, 'login.html')
        except User_admin.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return render(request, 'login.html')

    return render(request, 'login.html')


@admin_permission_required('control_servicios')
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

    # Los servicios oficiales están definidos en código fuente (app1/services_data.py)
    # y no son modificables desde el panel.
    if request.method == 'POST':
        messages.info(
            request,
            'Los servicios oficiales de RauDie están definidos en código (app1/services_data.py) '
            'para mantener la identidad visual y no son modificables desde el panel.'
        )
        return redirect('control_servicios')

    from app1.services_data import get_servicios
    servicios = get_servicios()
    return render(request, 'control_servicios.html', {
        'servicios': servicios,
        'user': user,
        'servicios_en_codigo': True
    })

# NUEVA/ACTUALIZADA: control_proyectos con manejo de categorias/tecnologias
@admin_permission_required('control_proyectos')
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
    if request.method == 'POST' and request.POST.get('crear_proyecto') == '1' and not request.POST.get('editar_proyecto_id'):
        titulo = request.POST.get('titulo', '').strip()
        cliente = request.POST.get('cliente', '').strip()
        fecha = request.POST.get('fecha', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        caracteristicas_txt = request.POST.get('caracteristicas', '').strip()
        archivos = request.FILES.getlist('fotos')
        categoria_ids = request.POST.getlist('categoria_ids') or request.POST.getlist('categoria_id')
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
                    if not f:
                        continue
                    saved_path = save_image_as_webp(f, 'proyectos')
                    try:
                        url = default_storage.url(saved_path)
                    except Exception:
                        url = settings.MEDIA_URL + saved_path
                    fotos_urls.append(url)
                # pasar listas de ids (pueden ser strings) al CRUD
                crear_proyecto(titulo, cliente, fecha_val, descripcion, caracteristicas, fotos_urls, categoria_ids=categoria_ids, tecnologia_ids=tecnologia_ids)
                messages.success(request, f'Proyecto creado correctamente con {len(fotos_urls)} imagen(es)')
                return redirect('control_proyectos')
            except ValueError:
                messages.error(request, 'Fecha inválida, use AAAA-MM-DD')

    # Editar proyecto
    if request.method == 'POST' and (request.POST.get('editar_proyecto') == '1' or request.POST.get('editar_proyecto_id')):
        proyecto_id = request.POST.get('editar_proyecto_id')
        titulo = request.POST.get('titulo', '').strip()
        cliente = request.POST.get('cliente', '').strip()
        fecha = request.POST.get('fecha', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        caracteristicas_txt = request.POST.get('caracteristicas', '').strip()
        archivos = request.FILES.getlist('fotos')
        categoria_ids = request.POST.getlist('categoria_ids') or request.POST.getlist('categoria_id')
        tecnologia_ids = request.POST.getlist('tecnologia_ids')

        if not proyecto_id:
            messages.error(request, 'ID de proyecto faltante')
        else:
            from datetime import datetime
            try:
                fecha_val = datetime.strptime(fecha, '%Y-%m-%d').date() if fecha else None
                caracteristicas = [c.strip() for c in caracteristicas_txt.split(',') if c.strip()] if caracteristicas_txt != '' else None
                # Conservar fotos existentes que el usuario mantuvo y agregar las nuevas subidas
                if 'gestion_fotos_activa' in request.POST:
                    fotos_urls = [u.strip() for u in request.POST.getlist('fotos_existentes') if u.strip()]
                else:
                    try:
                        proy_actual = Proyecto.objects.get(id=proyecto_id)
                        fotos_urls = list(proy_actual.fotos or [])
                    except Proyecto.DoesNotExist:
                        fotos_urls = []

                if archivos:
                    for f in archivos:
                        if not f:
                            continue
                        saved_path = save_image_as_webp(f, 'proyectos')
                        try:
                            url = default_storage.url(saved_path)
                        except Exception:
                            url = settings.MEDIA_URL + saved_path
                        fotos_urls.append(url)

                actualizar_proyecto(
                    proyecto_id,
                    titulo=titulo or None,
                    cliente=cliente or None,
                    fecha=fecha_val,
                    descripcion=descripcion or None,
                    caracteristicas=caracteristicas,
                    fotos=fotos_urls,
                    categoria_ids=categoria_ids if categoria_ids != [] else None,
                    tecnologia_ids=tecnologia_ids if tecnologia_ids != [] else None,
                )
                messages.success(request, f'Proyecto actualizado ({len(fotos_urls)} imagen(es) en galería)')
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
    return render(request, 'control_proyectos.html', {'proyectos': proyectos, 'categorias': categorias, 'tecnologias': tecnologias, 'user': user})

def logout(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada')
    return redirect('login')


# --- HELPER FUNCTIONS FOR BOT ---

def _get_session_user(request):
    uid = request.session.get('user_admin_id')
    if not uid:
        return None
    try:
        return User_admin.objects.get(id=uid)
    except User_admin.DoesNotExist:
        return None

def _get_public_bot():
    bot = ConfigBot.objects.filter(owner__isnull=True).first()
    if bot:
        return bot
    return ConfigBot.objects.first()

def _load_context_from_bot(bot):
    context_items = []
    allowed_exts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
    for context_file in bot.context_files.all():
        file_path = context_file.file.path
        filename = os.path.basename(context_file.file.name)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_exts:
            continue
        try:
            if ext == '.pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ''
                    for page in reader.pages[:3]:
                        text += page.extract_text() or ''
                    text = text.strip().replace('\r', '')
                    if text:
                        context_items.append(f"[PDF: {filename}]\n{text[:1500]}")
            elif ext in ['.docx']:
                doc = docx.Document(file_path)
                text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
                if text:
                    context_items.append(f"[Word: {filename}]\n{text[:1500]}")
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path, nrows=20)
                text = df.to_string(index=False)
                if text:
                    context_items.append(f"[Excel: {filename}]\n{text[:1500]}")
        except Exception as e:
            context_items.append(f"[Error leyendo {filename}]: {e}")
    context_str = "\n\n".join(context_items)
    return context_str

def _render_html_to_pdf(html_string):
    """
    Renders HTML to PDF bytes.
    Tries WeasyPrint first. If WeasyPrint fails (e.g. missing GTK/GObject on Windows),
    falls back gracefully to xhtml2pdf with CSS sanitization.
    """
    try:
        from weasyprint import HTML
        return HTML(string=html_string).write_pdf()
    except (OSError, ImportError, Exception) as weasy_err:
        try:
            import re
            from io import BytesIO
            from xhtml2pdf import pisa
            
            # Remove nested @at-rules inside @page (like @bottom-right) which crash xhtml2pdf's parser
            cleaned_html = re.sub(r'@[a-z-]+\s*\{[^{}]*\}', '', html_string)
            
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(cleaned_html.encode("UTF-8")), result)
            if not pdf.err:
                return result.getvalue()
            raise Exception(f"xhtml2pdf error code: {pdf.err}")
        except Exception as xhtml_err:
            raise Exception(
                f"No se pudo generar PDF. (WeasyPrint: {weasy_err} | Fallback xhtml2pdf: {xhtml_err})"
            )

def _generar_pdf_consulta(historial, datos_cliente, plan, departamento, resumen_ia=''):
    from django.template.loader import render_to_string
    from django.utils.timezone import now
    import random

    fecha = now().strftime('%d/%m/%Y %H:%M')
    referencia = now().strftime('%Y%m%d') + str(random.randint(100, 999))

    html = render_to_string('pdf_consulta.html', {
        'datos': datos_cliente,
        'plan': plan,
        'departamento': departamento,
        'resumen_ia': resumen_ia,
        'historial': historial,
        'fecha': fecha,
        'referencia': referencia,
    })

    pdf_bytes = _render_html_to_pdf(html)

    if not pdf_bytes:
        raise Exception("PDF vacío generado")
    
    return pdf_bytes


# --- BOT AND AGENTS VIEWS ---

@admin_permission_required('estado')
def estado(request):
    user = _get_session_user(request)
    if not user:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')

    bot = ConfigBot.objects.filter(owner=user).first()
    bot_statuses = []

    if bot:
        bot_status = 'connected' if bot.telegram_bot_token else 'disconnected'
        bot_statuses.append({
            'bot': bot,
            'status': bot_status
        })

    # Métricas y Datos Operativos en Tiempo Real
    total_contactos = Contacto.objects.count()
    ultimos_contactos = Contacto.objects.order_by('-fecha_creacion')[:6]

    total_proyectos = Proyecto.objects.count()
    ultimos_proyectos = Proyecto.objects.prefetch_related('categorias', 'tecnologias').order_by('-id')[:4]

    total_noticias = Noticia.objects.count()
    ultimas_noticias = Noticia.objects.order_by('-fecha', '-id')[:3]

    # Finanzas
    finanzas_ingresos = IncomeRecord.objects.aggregate(total=Sum('monto_usd'))['total'] or 0
    finanzas_gastos = ExpenseRecord.objects.aggregate(total=Sum('monto_usd'))['total'] or 0
    balance_neto = finanzas_ingresos - finanzas_gastos

    # Marketing / Contenido
    from django.utils import timezone
    hoy = timezone.now().date()
    proximas_publicaciones = PublicacionMarketing.objects.filter(fecha__gte=hoy).order_by('fecha')[:4]
    if not proximas_publicaciones.exists():
        proximas_publicaciones = PublicacionMarketing.objects.order_by('-fecha')[:4]
    total_marketing = PublicacionMarketing.objects.count()

    total_usuarios = User_admin.objects.count()
    total_mensajes_bot = TelegramMessage.objects.filter(bot=bot).count() if bot else 0

    context = {
        'user': user,
        'bot_statuses': bot_statuses,
        'bot': bot,
        'total_contactos': total_contactos,
        'ultimos_contactos': ultimos_contactos,
        'total_proyectos': total_proyectos,
        'ultimos_proyectos': ultimos_proyectos,
        'total_noticias': total_noticias,
        'ultimas_noticias': ultimas_noticias,
        'finanzas_ingresos': finanzas_ingresos,
        'finanzas_gastos': finanzas_gastos,
        'balance_neto': balance_neto,
        'total_marketing': total_marketing,
        'proximas_publicaciones': proximas_publicaciones,
        'total_usuarios': total_usuarios,
        'total_mensajes_bot': total_mensajes_bot,
        'fecha_hoy': hoy,
    }

    return render(request, 'control.html', context)

@admin_permission_required('configuracion')
def configuracion(request):
    user = _get_session_user(request)
    if not user:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')

    bot = ConfigBot.objects.filter(owner=user).first()

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        mensaje_bienvenida = request.POST.get('mensaje_bienvenida', '').strip()
        instrucciones_ia = request.POST.get('instrucciones_ia', '').strip()
        api_key = request.POST.get('api_key', '').strip()
        api_provider = request.POST.get('api_provider', 'deepseek')
        max_response_chars = int(request.POST.get('max_response_chars', 1000))
        inactividad_minutos = int(request.POST.get('inactividad_minutos', 0))
        mensaje_cierre = request.POST.get('mensaje_cierre', '').strip()

        if bot:
            bot.nombre = nombre
            bot.mensaje_bienvenida = mensaje_bienvenida
            bot.instrucciones_ia = instrucciones_ia
            if api_key:
                bot.api_key = encrypt_value(api_key)
            bot.api_provider = api_provider
            bot.max_response_chars = max_response_chars
            bot.inactividad_minutos = inactividad_minutos
            bot.mensaje_cierre = mensaje_cierre
            bot.save()
            messages.success(request, 'Configuración del bot actualizada correctamente.')
        else:
            bot = ConfigBot.objects.create(
                nombre=nombre,
                owner=user,
                mensaje_bienvenida=mensaje_bienvenida,
                instrucciones_ia=instrucciones_ia,
                api_key=encrypt_value(api_key) if api_key else '',
                api_provider=api_provider,
                max_response_chars=max_response_chars,
                inactividad_minutos=inactividad_minutos,
                mensaje_cierre=mensaje_cierre,
            )
            messages.success(request, 'Bot configurado correctamente. Ahora puedes conectar Telegram cuando quieras.')

        if 'context_files' in request.FILES:
            files = request.FILES.getlist('context_files')
            uploaded_count = 0
            for file in files:
                allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
                if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                    messages.error(request, f'Archivo {file.name} no permitido. Solo PDF, Word y Excel.')
                    continue
                ContextFile.objects.create(bot=bot, file=file)
                uploaded_count += 1
            if uploaded_count > 0:
                messages.success(request, f'Subidos {uploaded_count} archivos de contexto.')

        delete_files = request.POST.getlist('delete_files')
        for file_id in delete_files:
            try:
                context_file = ContextFile.objects.get(id=file_id, bot=bot)
                context_file.file.delete()
                context_file.delete()
                messages.success(request, f'Archivo eliminado.')
            except ContextFile.DoesNotExist:
                pass
        
        return redirect('configuracion')

    # Filtrar solo archivos que existen en disco y limpiar registros huérfanos
    context_files = []
    if bot:
        for cf in bot.context_files.all():
            try:
                if cf.file and os.path.exists(cf.file.path):
                    context_files.append(cf)
                else:
                    cf.delete()
            except Exception:
                cf.delete()

    return render(request, 'configuracion.html', {
        'bot': bot,
        'bot_status': 'unknown',
        'user': user,
        'context_files': context_files,
        'api_key_plain': decrypt_value(bot.api_key) if (bot and bot.api_key) else ''
    })

@admin_permission_required('telegram_configuracion')
def telegram_configuracion(request):
    from django.urls import reverse
    user = _get_session_user(request)
    if not user:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')

    bot = ConfigBot.objects.filter(owner=user).first()
    if not bot:
        messages.error(request, 'Guarda primero la configuración general del bot antes de conectar Telegram.')
        return redirect('configuracion')

    bot_info = None
    webhook_info = None
    error_msg = None

    if request.method == 'POST':
        if 'unlink' in request.POST:
            # Delete webhook from Telegram first
            if bot.telegram_bot_token:
                try:
                    requests.post(f"https://api.telegram.org/bot{bot.telegram_bot_token}/deleteWebhook", timeout=5)
                except Exception:
                    pass
            bot.telegram_bot_token = None
            bot.save()
            messages.success(request, 'Bot de Telegram desvinculado correctamente.')
            return redirect('telegram_configuracion')
        
        if 'update_webhook' in request.POST:
            webhook_url = request.POST.get('webhook_url', '').strip()
            if not bot.telegram_bot_token:
                messages.error(request, 'Debe configurar primero el Token del Bot.')
                return redirect('telegram_configuracion')
            
            try:
                if webhook_url:
                    if not (webhook_url.startswith('https://') or webhook_url.startswith('http://')):
                        webhook_url = 'https://' + webhook_url
                    
                    w_resp = requests.post(f"https://api.telegram.org/bot{bot.telegram_bot_token}/setWebhook", json={'url': webhook_url}, timeout=5)
                    if w_resp.status_code == 200:
                        messages.success(request, f'¡Webhook de Telegram configurado con éxito a: {webhook_url}!')
                    else:
                        messages.error(request, f'Error al registrar el webhook en Telegram: {w_resp.text}')
                else:
                    w_resp = requests.post(f"https://api.telegram.org/bot{bot.telegram_bot_token}/deleteWebhook", timeout=5)
                    if w_resp.status_code == 200:
                        messages.success(request, 'Webhook eliminado correctamente de Telegram.')
                    else:
                        messages.error(request, f'Error al eliminar el webhook: {w_resp.text}')
            except Exception as e:
                messages.error(request, f'Error al configurar el webhook: {e}')
            return redirect('telegram_configuracion')

        token = request.POST.get('telegram_bot_token', '').strip()
        if token:
            # Validate token using Telegram getMe
            try:
                resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
                if resp.status_code == 200:
                    bot.telegram_bot_token = token
                    bot.save()
                    messages.success(request, '¡Token de Telegram guardado y verificado con éxito!')
                    
                    # Set webhook automatically
                    webhook_url = request.build_absolute_uri(reverse('telegram_webhook', kwargs={'bot_id': bot.id}))
                    if webhook_url.startswith('http://127.0.0.1') or webhook_url.startswith('http://localhost'):
                        messages.warning(request, f'Estás en desarrollo local. Deberás usar una herramienta como ngrok para exponer tu puerto y registrar manualmente el webhook: {webhook_url}')
                    else:
                        if webhook_url.startswith('http://'):
                            webhook_url = webhook_url.replace('http://', 'https://')
                        w_resp = requests.post(f"https://api.telegram.org/bot{token}/setWebhook", json={'url': webhook_url}, timeout=5)
                        if w_resp.status_code == 200:
                            messages.success(request, 'Webhook de Telegram registrado automáticamente.')
                        else:
                            messages.error(request, f'No se pudo registrar el webhook automáticamente: {w_resp.text}')
                else:
                    error_msg = 'El token ingresado no es válido para Telegram (respuesta no exitosa de getMe).'
                    messages.error(request, error_msg)
            except Exception as e:
                error_msg = f'Error al intentar conectar con la API de Telegram: {e}'
                messages.error(request, error_msg)
        else:
            messages.error(request, 'Por favor, ingresa un token válido.')
        return redirect('telegram_configuracion')

    # Query bot info if token is configured
    if bot.telegram_bot_token:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{bot.telegram_bot_token}/getMe", timeout=5)
            if resp.status_code == 200:
                bot_info = resp.json().get('result')
                
                # Query webhook info
                w_resp = requests.get(f"https://api.telegram.org/bot{bot.telegram_bot_token}/getWebhookInfo", timeout=5)
                if w_resp.status_code == 200:
                    webhook_info = w_resp.json().get('result')
            else:
                error_msg = 'El token guardado no es válido (getMe falló). Por favor, configúralo de nuevo.'
        except Exception as e:
            error_msg = f'No se pudo conectar con la API de Telegram: {e}'

    # Suggest webhook URL
    suggested_webhook_url = request.build_absolute_uri(reverse('telegram_webhook', kwargs={'bot_id': bot.id}))
    if suggested_webhook_url.startswith('http://'):
        # Telegram webhook requires HTTPS
        suggested_webhook_url = suggested_webhook_url.replace('http://', 'https://')

    return render(request, 'telegram_configuracion.html', {
        'bot': bot,
        'bot_info': bot_info,
        'webhook_info': webhook_info,
        'error_msg': error_msg,
        'suggested_webhook_url': suggested_webhook_url,
        'user': user
    })

def create_edit_bot(request, bot_id=None):
    return redirect('configuracion')

def delete_bot(request, bot_id):
    user = _get_session_user(request)
    if not user:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')

    try:
        bot = ConfigBot.objects.get(id=bot_id, owner=user)
        bot.delete()
        messages.success(request, 'Bot eliminado correctamente')
    except ConfigBot.DoesNotExist:
        messages.error(request, 'Bot no encontrado')

    return redirect('configuracion')

@require_POST
@csrf_exempt
def enviar_reclamo(request):
    nombre = request.POST.get('nombre', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    if not nombre or not descripcion:
        return JsonResponse({'ok': False, 'error': 'Nombre y descripción son obligatorios.'})
    
    cuerpo = f"""
    Se ha recibido un nuevo reclamo/reporte desde la web:

    Nombre: {nombre}
    Teléfono: {telefono}
    Descripción: {descripcion}
    """
    email = EmailMessage(
        subject='Nuevo reclamo o reporte desde la web',
        body=cuerpo,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['sergio@syagroupchile.com', 'contacto@syagroup-chile.com']
    )
    try:
        email.send()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': 'No se pudo enviar el correo. ' + str(e)})

@ratelimit(key='ip', rate='20/m', method='POST', block=True)
def public_chat(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST allowed')

    message = request.POST.get('message', '').strip()
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if not message:
        return JsonResponse({'ok': False, 'error': 'Mensaje vacío'}, status=400)

    bot = _get_public_bot()
    if not bot:
        return JsonResponse({'ok': False, 'error': 'No hay bot configurado.'}, status=500)

    if not bot.api_key or not bot.instrucciones_ia:
        return JsonResponse({'ok': False, 'error': 'Bot sin configuración de IA.'}, status=500)

    # Verificar si ya fue transferido
    ya_transferido = TelegramMessage.objects.filter(
        bot=bot,
        chat_id=session_key,
        transferido=True
    ).exists()

    if ya_transferido:
        return JsonResponse({
            'ok': True,
            'reply': 'Tu consulta ya fue transferida a un asesor. En breve te contactarán.'
        })

    # Sanitizar mensaje
    message = re.sub(r'<<TRANSFERIR[^>]*>>', '', message).strip()
    message = re.sub(r'<<[A-Z_]+[^>]*>>', '', message).strip()

    if not message:
        return JsonResponse({'ok': False, 'error': 'Mensaje inválido.'}, status=400)

    # Guardar mensaje entrante
    TelegramMessage.objects.create(
        bot=bot,
        chat_id=session_key,
        push_name='Web',
        message_text=message
    )

    # Cargar historial completo
    historial = TelegramMessage.objects.filter(
        bot=bot,
        chat_id=session_key
    ).order_by('received_at')

    # Contexto de archivos
    context_text = _load_context_from_bot(bot)

    # Cargar departamentos disponibles
    departamentos_disponibles = Departamento.objects.filter(owner=bot.owner)
    dptos_texto = ""
    if departamentos_disponibles.exists():
        dptos_texto = "\n\nDEPARTAMENTOS DISPONIBLES PARA TRANSFERENCIA:\n"
        for dpto in departamentos_disponibles:
            desc = f" — {dpto.descripcion}" if dpto.descripcion else ""
            dptos_texto += f"- {dpto.nombre.lower()}{desc}\n"
        dptos_texto += (
            "\nCuando debas transferir usa exactamente:\n"
            "<<TRANSFERIR:nombre_departamento>>\n"
            "Donde nombre_departamento es uno de los listados arriba en minúscula."
        )

    api_key_plain = decrypt_value(bot.api_key) if bot.api_key else ''
    max_chars = getattr(bot, 'max_response_chars', 1000) or 1000

    system_content = bot.instrucciones_ia.strip()
    system_content += f'\n\nIMPORTANTE: Cada respuesta tuya debe tener MÁXIMO {max_chars} caracteres. Si necesitas listar servicios, menciona solo los más relevantes para la consulta del cliente, no todos.'
    if context_text:
        system_content += f"\n\nArchivos de contexto:\n{context_text}"
    if dptos_texto:
        system_content += dptos_texto

    # Construir mensajes con historial
    messages_ia = [{"role": "system", "content": system_content}]
    for msg in historial:
        if msg.message_text:
            messages_ia.append({"role": "user", "content": msg.message_text})
        if msg.reply_text:
            messages_ia.append({"role": "assistant", "content": msg.reply_text})

    # Llamar a DeepSeek
    try:
        resp = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            json={"model": "deepseek-chat", "messages": messages_ia},
            headers={
                'Authorization': f'Bearer {api_key_plain}',
                'Content-Type': 'application/json'
            },
            timeout=15
        )
        resp.raise_for_status()
        raw_reply = resp.json()['choices'][0]['message']['content'].strip()
        if max_chars and len(raw_reply) > max_chars:
            raw_reply = raw_reply[:max_chars].rsplit(' ', 1)[0] + '…'
    except Exception as e:
        print('[DeepSeek error]', e)
        return JsonResponse({'ok': False, 'error': f'Error IA: {e}'}, status=500)

    # Detectar flag de transferencia
    match = re.search(r'<<TRANSFERIR:([^>]+)>>', raw_reply)
    match_simple = re.search(r'<<TRANSFERIR>>', raw_reply)
    reply_limpio = re.sub(r'<<TRANSFERIR:[^>]+>>', '', raw_reply).strip()
    reply_limpio = re.sub(r'<<TRANSFERIR>>', '', reply_limpio).strip()

    # Guardar respuesta
    ultimo = TelegramMessage.objects.filter(
        bot=bot,
        chat_id=session_key,
        reply_text__isnull=True
    ).order_by('-received_at').first()
    if ultimo:
        ultimo.reply_text = reply_limpio
        ultimo.replied = True
        ultimo.replied_at = now()
        ultimo.save()

    # Procesar transferencia
    if match or match_simple:
        dpto_nombre = match.group(1).strip() if match else ''
        print('[DEBUG] Transferencia activada, dpto:', dpto_nombre)

        try:
            conv_check = ""
            for msg in TelegramMessage.objects.filter(bot=bot, chat_id=session_key).order_by('received_at'):
                if msg.message_text:
                    conv_check += msg.message_text + " "
                if msg.reply_text:
                    conv_check += msg.reply_text + " "

            tiene_correo   = bool(re.search(r'[\w.-]+@[\w.-]+\.\w+', conv_check))
            tiene_telefono = bool(re.search(r'[\+\d][\d\s\-]{7,}', conv_check))
            tiene_nombre   = len(conv_check.strip().split()) > 10  # conversación de longitud básica

            if not (tiene_correo and tiene_telefono and tiene_nombre):
                print('[Transferencia] Datos insuficientes, bloqueando transferencia.')
                return JsonResponse({'ok': True, 'reply': reply_limpio})

            agentes_destino = []
            if dpto_nombre:
                agentes_destino = list(Agente.objects.filter(
                    departamentos__nombre__iexact=dpto_nombre,
                    activo=True,
                    owner=bot.owner
                ).prefetch_related('departamentos'))

            if not agentes_destino:
                agentes_destino = list(Agente.objects.filter(
                    activo=True,
                    owner=bot.owner
                ).prefetch_related('departamentos'))

            if agentes_destino:
                historial_completo = TelegramMessage.objects.filter(bot=bot, chat_id=session_key).order_by('received_at')
                conv_texto = ""
                for msg in historial_completo:
                    if msg.message_text:
                        conv_texto += f"Cliente: {msg.message_text}\n"
                    if msg.reply_text:
                        conv_texto += f"Bot: {msg.reply_text}\n"

                datos_cliente = {
                    'nombre': '', 'correo': '', 'telefono': '',
                    'empresa': '', 'plan_interes': '', 'volumen_reportes': ''
                }
                try:
                    extraction_resp = requests.post(
                        'https://api.deepseek.com/v1/chat/completions',
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": (
                                    "Eres un extractor de datos. A partir de la conversación extrae "
                                    "los datos del cliente en JSON con claves exactas: "
                                    "nombre, correo, teléfono, empresa, plan_interes, volumen_reportes. "
                                    "Si un dato no aparece usa string vacío. "
                                    "Responde SOLO el JSON sin markdown ni explicaciones."
                                )},
                                {"role": "user", "content": conv_texto}
                            ]
                        },
                        headers={
                            'Authorization': f'Bearer {api_key_plain}',
                            'Content-Type': 'application/json'
                        },
                        timeout=15
                    )
                    if extraction_resp.status_code == 200:
                        raw = extraction_resp.json()['choices'][0]['message']['content']
                        raw = raw.strip().strip('```json').strip('```').strip()
                        datos_cliente = json_mod.loads(raw)
                except Exception as ex:
                    print('[Extracción datos error]', ex)

                plan_interes = datos_cliente.get('plan_interes') or 'No especificado'
                pdf_bytes = None
                filename = 'consulta.pdf'
                resumen_ia = ''

                try:
                    resumen_resp = requests.post(
                        'https://api.deepseek.com/v1/chat/completions',
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": (
                                    "Eres un asistente de ventas. Resume en 2-3 oraciones "
                                    "el perfil del cliente y su necesidad principal, "
                                    "destacando urgencia y oportunidad comercial. "
                                    "Sin markdown, texto plano."
                                )},
                                {"role": "user", "content": conv_texto}
                            ]
                        },
                        headers={
                            'Authorization': f'Bearer {api_key_plain}',
                            'Content-Type': 'application/json'
                        },
                        timeout=10
                    )
                    if resumen_resp.status_code == 200:
                        resumen_ia = resumen_resp.json()['choices'][0]['message']['content'].strip()
                except Exception as ex:
                    print('[Resumen IA error]', ex)

                try:
                    pdf_bytes = _generar_pdf_consulta(
                        historial_completo, datos_cliente, plan_interes,
                        dpto_nombre or 'General', resumen_ia
                    )
                    nombre_archivo = datos_cliente.get('nombre', 'cliente').replace(' ', '_')
                    filename = f"consulta_{nombre_archivo}.pdf"
                except Exception as ex:
                    print('[PDF error]', ex)

                mensaje_agente = (
                    f"NUEVA CONSULTA — {plan_interes}\n"
                    f"Fecha: {now().strftime('%d/%m/%Y %H:%M')}\n"
                    f"Departamento: {dpto_nombre or 'General'}\n\n"
                    f"DATOS DEL CLIENTE\n"
                    f"Nombre:   {datos_cliente.get('nombre') or 'No proporcionado'}\n"
                    f"Correo:   {datos_cliente.get('correo') or 'No proporcionado'}\n"
                    f"Teléfono: {datos_cliente.get('telefono') or 'No proporcionado'}\n"
                    f"Empresa:  {datos_cliente.get('empresa') or 'Particular'}\n\n"
                    f"PERFIL COMERCIAL\n"
                    f"Plan de interés:    {plan_interes}\n"
                    f"Volumen reportes:   {datos_cliente.get('volumen_reportes') or 'No especificado'}\n\n"
                    f"Historial completo adjunto."
                )

                for agente in agentes_destino:
                    tg_id = agente.telegram_id.strip() if agente.telegram_id else ''
                    if not tg_id:
                        continue
                    try:
                        if pdf_bytes:
                            # Send document to agent via Telegram Bot API
                            files = {'document': (filename, pdf_bytes, 'application/pdf')}
                            data = {'chat_id': tg_id, 'caption': mensaje_agente}
                            requests.post(
                                f"https://api.telegram.org/bot{bot.telegram_bot_token}/sendDocument",
                                data=data,
                                files=files,
                                timeout=20
                            )
                        else:
                            # Send plain text message
                            requests.post(
                                f"https://api.telegram.org/bot{bot.telegram_bot_token}/sendMessage",
                                json={'chat_id': tg_id, 'text': mensaje_agente},
                                timeout=10
                            )
                    except Exception as ex:
                        print(f'[Transferencia] Error enviando a agente {agente.nombre} via Telegram:', ex)

        except Exception as e:
            print('[Transferencia web error]', e)

        TelegramMessage.objects.filter(bot=bot, chat_id=session_key).update(transferido=True)

    return JsonResponse({'ok': True, 'reply': reply_limpio})

@csrf_exempt
def telegram_webhook(request, bot_id):
    from django.utils.timezone import now
    config = get_object_or_404(ConfigBot, id=bot_id)
    if not config.telegram_bot_token:
        return JsonResponse({'error': 'Bot sin token de Telegram.'}, status=400)

    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST allowed')

    try:
        data = json_mod.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    # Telegram sends updates to webhook
    message = data.get('message', {})
    if not message:
        return JsonResponse({'ok': True})  # ignore non-message updates (e.g. edited, callback queries)

    chat = message.get('chat', {})
    chat_id = str(chat.get('id', ''))
    text = message.get('text', '').strip()
    from_user = message.get('from', {})
    username = from_user.get('username', '')
    first_name = from_user.get('first_name', '')
    push_name = username or first_name or chat_id

    if not chat_id or not text:
        return JsonResponse({'ok': True})

    # 1. Handle /start command (return Chat ID to agent or user)
    if text == '/start':
        reply_msg = (
            f"¡Hola! Tu Chat ID de Telegram es: `{chat_id}`.\n\n"
            "Cópialo y colócalo en el panel de agentes del bot para poder recibir "
            "las notificaciones y derivaciones de prospectos."
        )
        try:
            requests.post(
                f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage",
                json={'chat_id': chat_id, 'text': reply_msg, 'parse_mode': 'Markdown'},
                timeout=10
            )
        except Exception as e:
            print("[Telegram Webhook /start error]", e)
        return JsonResponse({'ok': True})

    # 2. Save incoming client message
    TelegramMessage.objects.create(bot=config, chat_id=chat_id, push_name=push_name, message_text=text)

    # 3. Retrieve conversation history
    historial = TelegramMessage.objects.filter(bot=config, chat_id=chat_id).order_by('received_at')

    # 4. Check if conversation has already been transferred
    if historial.filter(transferido=True).exists():
        return JsonResponse({'ok': True})

    # 5. Build prompt / system messages
    instrucciones = config.instrucciones_ia if config else ''
    api_key_plain = decrypt_value(config.api_key) if config and config.api_key else ''
    max_chars = getattr(config, 'max_response_chars', 1000) or 1000
    context_text = _load_context_from_bot(config)

    departamentos_disponibles = Departamento.objects.filter(owner=config.owner)
    dptos_texto = ""
    if departamentos_disponibles.exists():
        dptos_texto = "\n\nDEPARTAMENTOS DISPONIBLES PARA TRANSFERENCIA:\n"
        for dpto in departamentos_disponibles:
            desc = f" — {dpto.descripcion}" if dpto.descripcion else ""
            dptos_texto += f"- {dpto.nombre.lower()}{desc}\n"
        dptos_texto += (
            "\nCuando debas transferir usa exactamente:\n"
            "<<TRANSFERIR:nombre_departamento>>\n"
            "Donde nombre_departamento es uno de los listados arriba en minúscula."
        )

    system_content = instrucciones.strip()
    system_content += f'\n\nIMPORTANTE: Cada respuesta tuya debe tener MÁXIMO {max_chars} caracteres. Si necesitas listar servicios, menciona solo los más relevantes para la consulta del cliente, no todos.'
    if context_text:
        system_content += f"\n\nArchivos de contexto:\n{context_text}"
    if dptos_texto:
        system_content += dptos_texto

    messages_ia = [{"role": "system", "content": system_content}]
    for msg in historial:
        if msg.message_text:
            messages_ia.append({"role": "user", "content": msg.message_text})
        if msg.reply_text:
            messages_ia.append({"role": "assistant", "content": msg.reply_text})

    reply = 'Gracias por tu mensaje. En breve te respondemos.'
    if api_key_plain and instrucciones:
        try:
            deepseek_url = 'https://api.deepseek.com/v1/chat/completions'
            headers = {
                'Authorization': f'Bearer {api_key_plain}',
                'Content-Type': 'application/json',
            }
            resp = requests.post(deepseek_url, json={"model": "deepseek-chat", "messages": messages_ia}, headers=headers, timeout=15)
            if resp.status_code == 200:
                res_data = resp.json()
                reply = res_data['choices'][0]['message']['content'].strip()
                if max_chars and len(reply) > max_chars:
                    reply = reply[:max_chars].rsplit(' ', 1)[0] + '…'
        except Exception as e:
            print('[DeepSeek Exception]', e)

    TRANSFER_FLAG = '<<TRANSFERIR>>'
    transferir = TRANSFER_FLAG in reply
    reply_limpio = reply.replace(TRANSFER_FLAG, '').strip()

    # 6. Send AI response back to client via Telegram
    try:
        requests.post(
            f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage",
            json={'chat_id': chat_id, 'text': reply_limpio},
            timeout=10
        )
    except Exception as e:
        print("[Telegram send AI reply error]", e)

    # 7. Save assistant reply
    ultimo = TelegramMessage.objects.filter(bot=config, chat_id=chat_id, reply_text__isnull=True).order_by('-received_at').first()
    if ultimo:
        ultimo.reply_text = reply_limpio
        ultimo.replied = True
        ultimo.replied_at = now()
        ultimo.save()

    # 8. Process Transfer to agents
    if transferir:
        try:
            dpto_nombre = None
            match = re.search(r'<<TRANSFERIR:([^>]+)>>', reply)
            if match:
                dpto_nombre = match.group(1).strip()

            agentes_destino = []
            if dpto_nombre:
                agentes_destino = list(Agente.objects.filter(
                    departamentos__nombre__iexact=dpto_nombre,
                    activo=True,
                    owner=config.owner
                ))
            if not agentes_destino:
                agentes_destino = list(Agente.objects.filter(
                    activo=True,
                    owner=config.owner
                ))

            # Check for name, email, phone in conversation history
            conv_check = ""
            for msg in historial:
                if msg.message_text:
                    conv_check += msg.message_text + " "
                if msg.reply_text:
                    conv_check += msg.reply_text + " "

            tiene_correo   = bool(re.search(r'[\w.-]+@[\w.-]+\.\w+', conv_check))
            tiene_telefono = bool(re.search(r'[\+\d][\d\s\-]{7,}', conv_check))
            tiene_nombre   = len(conv_check.strip().split()) > 10

            if not (tiene_correo and tiene_telefono and tiene_nombre):
                print('[Transferencia webhook] Datos insuficientes, cancelando.')
                return JsonResponse({'ok': True})

            datos_cliente = {
                'nombre': '', 'correo': '', 'telefono': '',
                'empresa': '', 'plan_interes': '', 'volumen_reportes': ''
            }
            try:
                extraction_resp = requests.post(
                    'https://api.deepseek.com/v1/chat/completions',
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": (
                                "Eres un extractor de datos. A partir de la conversación extrae "
                                "los datos del cliente en JSON con claves exactas: "
                                "nombre, correo, teléfono, empresa, plan_interes, volumen_reportes. "
                                "Si un dato no aparece usa string vacío. "
                                "Responde SOLO el JSON sin markdown ni explicaciones."
                            )},
                            {"role": "user", "content": conv_check}
                        ]
                    },
                    headers={
                        'Authorization': f'Bearer {api_key_plain}',
                        'Content-Type': 'application/json'
                    },
                    timeout=15
                )
                if extraction_resp.status_code == 200:
                    raw = extraction_resp.json()['choices'][0]['message']['content']
                    raw = raw.strip().strip('```json').strip('```').strip()
                    datos_cliente = json_mod.loads(raw)
            except Exception as ex:
                print('[Webhook Extracción datos error]', ex)

            plan_interes = datos_cliente.get('plan_interes') or 'No especificado'
            pdf_bytes = None
            filename = 'consulta.pdf'
            resumen_ia = ''

            try:
                resumen_resp = requests.post(
                    'https://api.deepseek.com/v1/chat/completions',
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": (
                                "Eres un asistente de ventas. Resume en 2-3 oraciones "
                                "el perfil del cliente y su necesidad principal, "
                                "destacando urgencia y oportunidad comercial. "
                                "Sin markdown, texto plano."
                            )},
                            {"role": "user", "content": conv_check}
                        ]
                    },
                    headers={
                        'Authorization': f'Bearer {api_key_plain}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10
                )
                if resumen_resp.status_code == 200:
                    resumen_ia = resumen_resp.json()['choices'][0]['message']['content'].strip()
            except Exception as ex:
                print('[Webhook Resumen IA error]', ex)

            try:
                pdf_bytes = _generar_pdf_consulta(
                    historial, datos_cliente, plan_interes,
                    dpto_nombre or 'General', resumen_ia
                )
                nombre_archivo = datos_cliente.get('nombre', 'cliente').replace(' ', '_')
                filename = f"consulta_{nombre_archivo}.pdf"
            except Exception as ex:
                print('[Webhook PDF error]', ex)

            mensaje_agente = (
                f"NUEVA CONSULTA — {plan_interes}\n"
                f"Cliente: {push_name}\n"
                f"Telegram Chat ID: {chat_id}\n\n"
                f"DATOS DEL CLIENTE\n"
                f"Nombre:   {datos_cliente.get('nombre') or 'No proporcionado'}\n"
                f"Correo:   {datos_cliente.get('correo') or 'No proporcionado'}\n"
                f"Teléfono: {datos_cliente.get('telefono') or 'No proporcionado'}\n"
                f"Empresa:  {datos_cliente.get('empresa') or 'Particular'}\n\n"
                f"PERFIL COMERCIAL\n"
                f"Plan de interés:    {plan_interes}\n"
                f"Volumen reportes:   {datos_cliente.get('volumen_reportes') or 'No especificado'}\n\n"
                f"Historial completo adjunto."
            )

            for agente in agentes_destino:
                tg_id = agente.telegram_id.strip() if agente.telegram_id else ''
                if not tg_id:
                    continue
                try:
                    if pdf_bytes:
                        files = {'document': (filename, pdf_bytes, 'application/pdf')}
                        data = {'chat_id': tg_id, 'caption': mensaje_agente}
                        requests.post(
                            f"https://api.telegram.org/bot{config.telegram_bot_token}/sendDocument",
                            data=data,
                            files=files,
                            timeout=20
                        )
                    else:
                        requests.post(
                            f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage",
                            json={'chat_id': tg_id, 'text': mensaje_agente},
                            timeout=10
                        )
                except Exception as ex:
                    print(f'[Transferencia webhook] Error enviando a agente {agente.nombre} via Telegram:', ex)

            TelegramMessage.objects.filter(bot=config, chat_id=chat_id).update(transferido=True)
        except Exception as e:
            print('[Webhook Transferencia error]', e)

    return JsonResponse({'ok': True})

def send_message(request):
    from django.utils.timezone import now
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST allowed')

    number = request.POST.get('number')  # chat_id of the user
    message = request.POST.get('message')
    from_url = request.META.get('HTTP_REFERER', '')
    is_config = 'configuracion' in from_url

    if not number or not message:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Faltan campos chat_id o message'}, status=400)
        messages.error(request, 'Faltan campos: ID de chat y mensaje')
        return redirect('configuracion' if is_config else 'panel_control')

    # Get session user bot
    user = _get_session_user(request)
    bot = ConfigBot.objects.filter(owner=user).first() if user else None
    if not bot or not bot.telegram_bot_token:
        err = 'Bot no configurado o sin token de Telegram.'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': err}, status=400)
        messages.error(request, err)
        return redirect('configuracion' if is_config else 'panel_control')

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot.telegram_bot_token}/sendMessage",
            json={'chat_id': number, 'text': message},
            timeout=8
        )
        resp.raise_for_status()

        # Save manual reply in conversation history
        TelegramMessage.objects.create(
            bot=bot,
            chat_id=number,
            push_name='Soporte',
            message_text='',
            reply_text=message,
            replied=True,
            replied_at=now()
        )
    except Exception as e:
        err = str(e)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': err}, status=500)
        messages.error(request, f'Error al enviar mensaje por Telegram: {err}')
        return redirect('configuracion' if is_config else 'panel_control')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    messages.success(request, 'Mensaje de Telegram enviado correctamente')
    return redirect('configuracion' if is_config else 'panel_control')

@admin_permission_required('departamentos')
def departamentos(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    dptos = Departamento.objects.filter(owner=user)
    return render(request, 'departamentos.html', {'departamentos': dptos, 'user': user})

@admin_permission_required('departamentos')
def departamento_crear(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        if nombre:
            Departamento.objects.create(nombre=nombre, descripcion=descripcion, owner=user)
            messages.success(request, 'Departamento creado.')
        return redirect('departamentos')
    return render(request, 'departamento_form.html', {'user': user})

@admin_permission_required('departamentos')
def departamento_editar(request, dpto_id):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    try:
        dpto = Departamento.objects.get(id=dpto_id, owner=user)
    except Departamento.DoesNotExist:
        messages.error(request, 'Departamento no encontrado.')
        return redirect('departamentos')
    if request.method == 'POST':
        dpto.nombre = request.POST.get('nombre', '').strip()
        dpto.descripcion = request.POST.get('descripcion', '').strip()
        dpto.save()
        messages.success(request, 'Departamento actualizado.')
        return redirect('departamentos')
    return render(request, 'departamento_form.html', {'dpto': dpto, 'user': user})

@admin_permission_required('departamentos')
def departamento_eliminar(request, dpto_id):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    try:
        dpto = Departamento.objects.get(id=dpto_id, owner=user)
        dpto.delete()
        messages.success(request, 'Departamento eliminado.')
    except Departamento.DoesNotExist:
        messages.error(request, 'Departamento no encontrado.')
    return redirect('departamentos')

@admin_permission_required('agentes')
def agentes(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    agentes_list = Agente.objects.filter(owner=user).prefetch_related('departamentos')
    return render(request, 'agentes.html', {'agentes': agentes_list, 'user': user})

@admin_permission_required('agentes')
def agente_crear(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    dptos = Departamento.objects.filter(owner=user)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        telegram_id = request.POST.get('telegram_id', '').strip()
        activo = request.POST.get('activo') == 'on'
        dptos_ids = request.POST.getlist('departamentos')
        agente = Agente.objects.create(
            nombre=nombre,
            telegram_id=telegram_id,
            activo=activo,
            owner=user
        )
        selected_dptos = Departamento.objects.filter(id__in=dptos_ids, owner=user)
        agente.departamentos.set(selected_dptos)
        messages.success(request, 'Agente creado.')
        return redirect('agentes')
    return render(request, 'agente_form.html', {'departamentos': dptos, 'user': user})

@admin_permission_required('agentes')
def agente_editar(request, agente_id):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    try:
        agente = Agente.objects.get(id=agente_id, owner=user)
    except Agente.DoesNotExist:
        messages.error(request, 'Agente no encontrado.')
        return redirect('agentes')
    dptos = Departamento.objects.filter(owner=user)
    if request.method == 'POST':
        agente.nombre = request.POST.get('nombre', '').strip()
        agente.telegram_id = request.POST.get('telegram_id', '').strip()
        agente.activo = request.POST.get('activo') == 'on'
        dptos_ids = request.POST.getlist('departamentos')
        selected_dptos = Departamento.objects.filter(id__in=dptos_ids, owner=user)
        agente.departamentos.set(selected_dptos)
        agente.save()
        messages.success(request, 'Agente actualizado.')
        return redirect('agentes')
    return render(request, 'agente_form.html', {'agente': agente, 'departamentos': dptos, 'user': user})

@admin_permission_required('agentes')
def agente_eliminar(request, agente_id):
    user = _get_session_user(request)
    if not user:
        return redirect('login')
    try:
        agente = Agente.objects.get(id=agente_id, owner=user)
        agente.delete()
        messages.success(request, 'Agente eliminado.')
    except Agente.DoesNotExist:
        messages.error(request, 'Agente no encontrado.')
    return redirect('agentes')

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def reset_chat(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST allowed')
    
    session_key = request.session.session_key
    if session_key:
        bot = _get_public_bot()
        if bot:
            TelegramMessage.objects.filter(bot=bot, chat_id=session_key).delete()
    
    return JsonResponse({'ok': True})

@require_POST
def queue_drain(request):
    """Devuelve éxito directamente ya que Telegram no requiere cola local."""
    return JsonResponse({'ok': True, 'message': 'Cola no requerida para Telegram'})

def queue_status(request):
    """Devuelve 0 mensajes pendientes para compatibilidad con la interfaz."""
    user = _get_session_user(request)
    bot = ConfigBot.objects.filter(owner=user).first() if user else None
    status = 'connected' if (bot and bot.telegram_bot_token) else 'disconnected'
    return JsonResponse({
        'ok': True,
        'status': status,
        'pending': 0,
    })


@admin_permission_required('conversaciones')
def conversaciones(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')

    bot = ConfigBot.objects.filter(owner=user).first()
    if not bot:
        return render(request, 'conversaciones.html', {'conversaciones': [], 'user': user})

    from django.db.models import Max, Count
    convs = TelegramMessage.objects.filter(
        bot=bot
    ).values(
        'chat_id', 'push_name'
    ).annotate(
        ultimo_mensaje=Max('received_at'),
        total_mensajes=Count('id'),
        transferido=Max('transferido')
    ).order_by('-ultimo_mensaje')

    if request.GET.get('json'):
        from django.utils.timezone import now
        hoy = now().date()
        mensajes_hoy = TelegramMessage.objects.filter(bot=bot, received_at__date=hoy).count()
        activas = convs.filter(transferido=False).count()
        transferidas = convs.filter(transferido=True).count()
        return JsonResponse({'mensajes_hoy': mensajes_hoy, 'activas': activas, 'transferidas': transferidas})
    
    return render(request, 'conversaciones.html', {
        'conversaciones': convs,
        'user': user,
        'bot': bot
    })


@admin_permission_required('conversaciones')
def conversacion_detalle(request, remote_jid):
    user = _get_session_user(request)
    if not user:
        return redirect('login')

    bot = ConfigBot.objects.filter(owner=user).first()
    if not bot:
        return redirect('conversaciones')

    import urllib.parse
    remote_jid_decoded = urllib.parse.unquote(remote_jid)

    mensajes = TelegramMessage.objects.filter(
        bot=bot, chat_id=remote_jid_decoded
    ).order_by('received_at')

    return render(request, 'conversacion_detalle.html', {
        'mensajes': mensajes,
        'remote_jid': remote_jid_decoded,
        'user': user,
        'bot': bot
    })
    

def perfil(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre', '').strip()
        password_actual = request.POST.get('password_actual', '')
        nuevo_password = request.POST.get('nuevo_password', '').strip()
        confirmar_password = request.POST.get('confirmar_password', '').strip()

        if nuevo_nombre and nuevo_nombre != user.nombre:
            if User_admin.objects.filter(nombre=nuevo_nombre).exclude(id=user.id).exists():
                messages.error(request, 'Ese nombre de usuario ya está en uso.')
                return redirect('perfil')
            user.nombre = nuevo_nombre
            user.save()
            messages.success(request, 'Nombre actualizado correctamente.')

        if nuevo_password:
            from django.contrib.auth.hashers import check_password, make_password
            if not check_password(password_actual, user.password):
                messages.error(request, 'Contraseña actual incorrecta.')
                return redirect('perfil')
            if nuevo_password != confirmar_password:
                messages.error(request, 'Las contraseñas nuevas no coinciden.')
                return redirect('perfil')
            if len(nuevo_password) < 6:
                messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                return redirect('perfil')
            user.password = make_password(nuevo_password)
            user.save()
            messages.success(request, 'Contraseña actualizada correctamente.')

        return redirect('perfil')

    return render(request, 'perfil.html', {'user': user})

def _seed_accounting_data():
    import os
    from datetime import datetime
    import openpyxl
    from django.conf import settings
    from .models import CostItem, ProjectHourlyRate, ProjectCostType, IncomeRecord, ExpenseRecord

    if CostItem.objects.exists() or IncomeRecord.objects.exists() or ExpenseRecord.objects.exists():
        return

    excel_path = os.path.join(settings.BASE_DIR, 'Radie contabilidad.xlsx')
    if not os.path.exists(excel_path):
        return

    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)

        if 'Estructura de costos' in wb.sheetnames:
            ws = wb['Estructura de costos']
            for r in range(3, 15):
                desc = ws.cell(r, 1).value
                price = ws.cell(r, 2).value
                if desc and price is not None:
                    CostItem.objects.get_or_create(
                        descripcion=str(desc).strip(),
                        precio=float(price)
                    )

            for r in range(3, 11):
                desc = ws.cell(r, 9).value
                hours = ws.cell(r, 10).value
                precio = ws.cell(r, 12).value
                if desc and hours is not None:
                    ProjectCostType.objects.get_or_create(
                        descripcion=str(desc).strip(),
                        horas=float(hours),
                        precio=float(precio) if precio is not None else 0.0
                    )

            rate_val = ws.cell(19, 2).value
            if rate_val is not None:
                ProjectHourlyRate.objects.get_or_create(rate=float(rate_val))
            else:
                ProjectHourlyRate.objects.get_or_create(rate=25.0)
        else:
            ProjectHourlyRate.objects.get_or_create(rate=25.0)

        if 'Ingresos cobros' in wb.sheetnames:
            ws = wb['Ingresos cobros']
            for r in range(2, 100):
                fecha = ws.cell(r, 1).value
                cliente = ws.cell(r, 2).value
                monto_usd = ws.cell(r, 3).value
                tasa_dia = ws.cell(r, 4).value
                total_bs = ws.cell(r, 5).value
                cobrada_val = ws.cell(r, 6).value
                cuota = ws.cell(r, 7).value

                if cliente is None and monto_usd is None:
                    continue

                date_val = None
                if isinstance(fecha, datetime):
                    date_val = fecha.date()
                elif isinstance(fecha, str):
                    try:
                        date_val = datetime.strptime(fecha.strip(), '%Y-%m-%d').date()
                    except ValueError:
                        pass

                cobrada_bool = True
                if cobrada_val:
                    cobrada_bool = str(cobrada_val).strip().lower() == 'si'

                m_usd = float(monto_usd) if monto_usd is not None else 0.0
                t_dia = float(tasa_dia) if tasa_dia is not None else 0.0
                t_bs = float(total_bs) if total_bs is not None else (m_usd * t_dia)

                IncomeRecord.objects.create(
                    fecha=date_val,
                    cliente=str(cliente or 'Sin Cliente').strip(),
                    monto_usd=m_usd,
                    tasa_dia=t_dia,
                    total_bs=t_bs,
                    cobrada=cobrada_bool,
                    cuota=float(cuota) if cuota is not None else None
                )

        if 'Gastos pagos' in wb.sheetnames:
            ws = wb['Gastos pagos']
            for r in range(2, 100):
                fecha = ws.cell(r, 1).value
                proveedor = ws.cell(r, 2).value
                monto_usd = ws.cell(r, 3).value
                tasa_dia = ws.cell(r, 4).value
                total_bs = ws.cell(r, 5).value
                pagada_val = ws.cell(r, 6).value
                fecha_credito = ws.cell(r, 7).value

                if proveedor is None and monto_usd is None:
                    continue

                date_val = None
                if isinstance(fecha, datetime):
                    date_val = fecha.date()
                elif isinstance(fecha, str):
                    try:
                        date_val = datetime.strptime(fecha.strip(), '%Y-%m-%d').date()
                    except ValueError:
                        pass

                pagada_bool = True
                if pagada_val:
                    pagada_bool = str(pagada_val).strip().lower() == 'si'

                cred_str = 'no aplica'
                if isinstance(fecha_credito, datetime):
                    cred_str = fecha_credito.strftime('%Y-%m-%d')
                elif fecha_credito is not None:
                    cred_str = str(fecha_credito).strip()

                m_usd = float(monto_usd) if monto_usd is not None else 0.0
                t_dia = float(tasa_dia) if tasa_dia is not None else 0.0
                t_bs = float(total_bs) if total_bs is not None else (m_usd * t_dia)

                ExpenseRecord.objects.create(
                    fecha=date_val,
                    proveedor=str(proveedor or 'Sin Proveedor').strip(),
                    monto_usd=m_usd,
                    tasa_dia=t_dia,
                    total_bs=t_bs,
                    pagada=pagada_bool,
                    fecha_credito=cred_str
                )

    except Exception as e:
        print('[Seeding Accounting Error]', e)


@admin_permission_required('contabilidad_costos')
def contabilidad_costos(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')

    _seed_accounting_data()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_rate':
            rate_val = request.POST.get('rate')
            if rate_val:
                ProjectHourlyRate.objects.all().delete()
                ProjectHourlyRate.objects.create(rate=float(rate_val))
                messages.success(request, 'Tarifa de venta por hora actualizada.')

        elif action == 'add_cost':
            desc = request.POST.get('descripcion')
            precio = request.POST.get('precio')
            if desc and precio:
                CostItem.objects.create(descripcion=desc.strip(), precio=float(precio))
                messages.success(request, 'Item de costo agregado.')

        elif action == 'edit_cost':
            cost_id = request.POST.get('cost_id')
            desc = request.POST.get('descripcion')
            precio = request.POST.get('precio')
            if cost_id and desc and precio:
                CostItem.objects.filter(id=cost_id).update(descripcion=desc.strip(), precio=float(precio))
                messages.success(request, 'Item de costo actualizado.')

        elif action == 'delete_cost':
            cost_id = request.POST.get('cost_id')
            if cost_id:
                CostItem.objects.filter(id=cost_id).delete()
                messages.success(request, 'Item de costo eliminado.')

        elif action == 'add_project':
            desc = request.POST.get('descripcion')
            horas = request.POST.get('horas')
            precio = request.POST.get('precio')
            if desc and horas:
                ProjectCostType.objects.create(
                    descripcion=desc.strip(),
                    horas=float(horas),
                    precio=float(precio) if precio else 0.0
                )
                messages.success(request, 'Proyecto de catálogo agregado.')

        elif action == 'edit_project':
            proj_id = request.POST.get('proj_id')
            desc = request.POST.get('descripcion')
            horas = request.POST.get('horas')
            precio = request.POST.get('precio')
            if proj_id and desc and horas:
                ProjectCostType.objects.filter(id=proj_id).update(
                    descripcion=desc.strip(),
                    horas=float(horas),
                    precio=float(precio) if precio else 0.0
                )
                messages.success(request, 'Proyecto de catálogo actualizado.')

        elif action == 'delete_project':
            proj_id = request.POST.get('proj_id')
            if proj_id:
                ProjectCostType.objects.filter(id=proj_id).delete()
                messages.success(request, 'Proyecto de catálogo eliminado.')

        return redirect('contabilidad_costos')

    costs = CostItem.objects.all()
    total_costos = sum(c.precio for c in costs)
    costo_por_hora_interno = total_costos / 160 if total_costos else 0.0

    rate_obj = ProjectHourlyRate.objects.last()
    if not rate_obj:
        rate_obj = ProjectHourlyRate.objects.create(rate=25.0)
    rate = rate_obj.rate

    max_ingreso = 160 * rate
    max_ganancia = max_ingreso - total_costos

    raw_projects = ProjectCostType.objects.all()
    projects = []
    for rp in raw_projects:
        costo = rp.horas * costo_por_hora_interno
        precio = rp.precio if rp.precio > 0.0 else (rp.horas * rate)
        ganancia = precio - costo
        projects.append({
            'id': rp.id,
            'descripcion': rp.descripcion,
            'horas': rp.horas,
            'costo': costo,
            'precio': precio,
            'precio_raw': rp.precio,
            'ganancia': ganancia
        })

    return render(request, 'contabilidad/costos.html', {
        'user': user,
        'costs': costs,
        'total_costos': total_costos,
        'costo_por_hora_interno': costo_por_hora_interno,
        'rate': rate,
        'max_ingreso': max_ingreso,
        'max_ganancia': max_ganancia,
        'projects': projects
    })


@admin_permission_required('contabilidad_finanzas')
def contabilidad_finanzas(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')

    _seed_accounting_data()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_income':
            fecha_str = request.POST.get('fecha')
            cliente = request.POST.get('cliente')
            monto_usd = request.POST.get('monto_usd')
            tasa_dia = request.POST.get('tasa_dia')
            cobrada = request.POST.get('cobrada') == 'on'
            cuota = request.POST.get('cuota')

            fecha = None
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            m_usd = float(monto_usd) if monto_usd else 0.0
            t_dia = float(tasa_dia) if tasa_dia else 0.0
            total_bs = m_usd * t_dia

            IncomeRecord.objects.create(
                fecha=fecha,
                cliente=cliente.strip(),
                monto_usd=m_usd,
                tasa_dia=t_dia,
                total_bs=total_bs,
                cobrada=cobrada,
                cuota=float(cuota) if cuota else None
            )
            messages.success(request, 'Cobro / Ingreso registrado.')

        elif action == 'edit_income':
            inc_id = request.POST.get('income_id')
            fecha_str = request.POST.get('fecha')
            cliente = request.POST.get('cliente')
            monto_usd = request.POST.get('monto_usd')
            tasa_dia = request.POST.get('tasa_dia')
            cobrada = request.POST.get('cobrada') == 'on'
            cuota = request.POST.get('cuota')

            fecha = None
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            m_usd = float(monto_usd) if monto_usd else 0.0
            t_dia = float(tasa_dia) if tasa_dia else 0.0
            total_bs = m_usd * t_dia

            IncomeRecord.objects.filter(id=inc_id).update(
                fecha=fecha,
                cliente=cliente.strip(),
                monto_usd=m_usd,
                tasa_dia=t_dia,
                total_bs=total_bs,
                cobrada=cobrada,
                cuota=float(cuota) if cuota else None
            )
            messages.success(request, 'Ingreso actualizado.')

        elif action == 'delete_income':
            inc_id = request.POST.get('income_id')
            if inc_id:
                IncomeRecord.objects.filter(id=inc_id).delete()
                messages.success(request, 'Ingreso eliminado.')

        elif action == 'add_expense':
            fecha_str = request.POST.get('fecha')
            proveedor = request.POST.get('proveedor')
            monto_usd = request.POST.get('monto_usd')
            tasa_dia = request.POST.get('tasa_dia')
            pagada = request.POST.get('pagada') == 'on'
            fecha_credito = request.POST.get('fecha_credito', 'no aplica')

            fecha = None
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            m_usd = float(monto_usd) if monto_usd else 0.0
            t_dia = float(tasa_dia) if tasa_dia else 0.0
            total_bs = m_usd * t_dia

            ExpenseRecord.objects.create(
                fecha=fecha,
                proveedor=proveedor.strip(),
                monto_usd=m_usd,
                tasa_dia=t_dia,
                total_bs=total_bs,
                pagada=pagada,
                fecha_credito=fecha_credito.strip() if fecha_credito else 'no aplica'
            )
            messages.success(request, 'Pago / Gasto registrado.')

        elif action == 'edit_expense':
            exp_id = request.POST.get('expense_id')
            fecha_str = request.POST.get('fecha')
            proveedor = request.POST.get('proveedor')
            monto_usd = request.POST.get('monto_usd')
            tasa_dia = request.POST.get('tasa_dia')
            pagada = request.POST.get('pagada') == 'on'
            fecha_credito = request.POST.get('fecha_credito', 'no aplica')

            fecha = None
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            m_usd = float(monto_usd) if monto_usd else 0.0
            t_dia = float(tasa_dia) if tasa_dia else 0.0
            total_bs = m_usd * t_dia

            ExpenseRecord.objects.filter(id=exp_id).update(
                fecha=fecha,
                proveedor=proveedor.strip(),
                monto_usd=m_usd,
                tasa_dia=t_dia,
                total_bs=total_bs,
                pagada=pagada,
                fecha_credito=fecha_credito.strip() if fecha_credito else 'no aplica'
            )
            messages.success(request, 'Gasto actualizado.')

        elif action == 'delete_expense':
            exp_id = request.POST.get('expense_id')
            if exp_id:
                ExpenseRecord.objects.filter(id=exp_id).delete()
                messages.success(request, 'Gasto eliminado.')

        return redirect('contabilidad_finanzas')

    incomes = IncomeRecord.objects.all().order_by('-fecha')
    expenses = ExpenseRecord.objects.all().order_by('-fecha')

    total_income_usd = sum(i.monto_usd for i in incomes)
    total_expense_usd = sum(e.monto_usd for e in expenses)
    balance_usd = total_income_usd - total_expense_usd

    total_income_bs = sum(i.total_bs for i in incomes)
    total_expense_bs = sum(e.total_bs for e in expenses)
    balance_bs = total_income_bs - total_expense_bs

    return render(request, 'contabilidad/finanzas.html', {
        'user': user,
        'incomes': incomes,
        'expenses': expenses,
        'total_income_usd': total_income_usd,
        'total_expense_usd': total_expense_usd,
        'balance_usd': balance_usd,
        'total_income_bs': total_income_bs,
        'total_expense_bs': total_expense_bs,
        'balance_bs': balance_bs
    })

@admin_permission_required('generar_cotizacion')
def generar_cotizacion(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')

    _seed_accounting_data()

    rate_obj = ProjectHourlyRate.objects.last()
    rate = rate_obj.rate if rate_obj else 25.0

    def _format_currency(val):
        if val is None:
            return "$0,00"
        formatted = f"{val:,.2f}"
        tbl = str.maketrans({',': '.', '.': ','})
        return "$" + formatted.translate(tbl)

    if request.method == 'POST':
        cliente = request.POST.get('cliente', '').strip()
        rif = request.POST.get('rif', '').strip()
        fecha_str = request.POST.get('fecha', '').strip()
        condiciones = request.POST.get('condiciones_pago', '').strip()

        conceptos = request.POST.getlist('conceptos[]')
        horas = request.POST.getlist('horas[]')
        importes = request.POST.getlist('importes[]')

        items = []
        total_importe = 0.0
        for i in range(len(conceptos)):
            if conceptos[i].strip():
                h_val = float(horas[i]) if i < len(horas) and horas[i] else 0.0
                imp_val = float(importes[i]) if i < len(importes) and importes[i] else (h_val * float(rate))
                items.append({
                    'descripcion': conceptos[i].strip(),
                    'horas': h_val,
                    'importe': imp_val,
                    'importe_formatted': _format_currency(imp_val)
                })
                total_importe += imp_val

        # Prepara fecha
        if fecha_str:
            try:
                parsed_date = datetime.strptime(fecha_str, '%Y-%m-%d')
                months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                          "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
                fecha_formatted = f"{parsed_date.day} de {months[parsed_date.month - 1]} de {parsed_date.year}"
            except ValueError:
                fecha_formatted = fecha_str
        else:
            parsed_date = datetime.now()
            months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                      "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            fecha_formatted = f"{parsed_date.day} de {months[parsed_date.month - 1]} de {parsed_date.year}"

        import random
        referencia = datetime.now().strftime('%Y%m%d') + str(random.randint(100, 999))

        logo_path = os.path.join(settings.BASE_DIR, 'assets', 'img', 'cotizaciones_logo.png')
        logo_uri = f"file:///{logo_path.replace('\\', '/')}"

        html = render_to_string('contabilidad/pdf_cotizacion.html', {
            'cliente': cliente,
            'rif': rif,
            'fecha': fecha_formatted,
            'referencia': referencia,
            'condiciones': condiciones,
            'items': items,
            'total_importe_formatted': _format_currency(total_importe),
            'logo_path': logo_path,
            'logo_uri': logo_uri
        })

        try:
            pdf_bytes = _render_html_to_pdf(html)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="cotizacion_{cliente.replace(" ", "_")}.pdf"'
            return response
        except Exception as e:
            return HttpResponse(f"Error generando PDF: {e}", status=500)

    # GET
    catalog = ProjectCostType.objects.all()
    default_conditions = "Cancela el 50% del presupuesto para empezar el proyecto y 50% restante al terminar"
    return render(request, 'contabilidad/cotizacion.html', {
        'user': user,
        'rate': rate,
        'catalog': catalog,
        'default_conditions': default_conditions,
        'today': datetime.now().strftime('%Y-%m-%d')
    })


@admin_permission_required('marketing')
def marketing_view(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')
    try:
        user = User_admin.objects.get(id=user_id)
    except User_admin.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')

    from datetime import date, timedelta
    from .models import PublicacionMarketing

    week_param = request.GET.get('week')
    today = date.today()

    if week_param:
        try:
            ref_date = datetime.strptime(week_param, '%Y-%m-%d').date()
        except ValueError:
            ref_date = today
    else:
        ref_date = today

    # Lunes de la semana seleccionada
    monday = ref_date - timedelta(days=ref_date.weekday())
    sunday = monday + timedelta(days=6)

    dias_semana = []
    nombres_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    for i in range(7):
        day_date = monday + timedelta(days=i)
        dias_semana.append({
            'nombre': nombres_dias[i],
            'fecha': day_date,
            'fecha_str': day_date.strftime('%Y-%m-%d'),
            'es_hoy': day_date == today,
            'publicaciones': []
        })

    publicaciones = PublicacionMarketing.objects.filter(
        owner=user,
        fecha__range=[monday, sunday]
    ).order_by('fecha', 'id')

    for pub in publicaciones:
        day_index = pub.fecha.weekday()
        dias_semana[day_index]['publicaciones'].append(pub)

    prev_week = (monday - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (monday + timedelta(days=7)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')

    return render(request, 'marketing.html', {
        'user': user,
        'dias_semana': dias_semana,
        'monday': monday,
        'sunday': sunday,
        'prev_week': prev_week,
        'next_week': next_week,
        'today_str': today_str,
        'current_week_str': monday.strftime('%Y-%m-%d'),
        'plataformas': PublicacionMarketing.PLATFORM_CHOICES,
        'formatos': PublicacionMarketing.FORMATO_CHOICES,
    })


@admin_permission_required('marketing')
def marketing_crear(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        return HttpResponse('No autorizado', status=401)

    if request.method == 'POST':
        from .models import PublicacionMarketing, User_admin
        try:
            user = User_admin.objects.get(id=user_id)
        except User_admin.DoesNotExist:
            return HttpResponse('Usuario no encontrado', status=404)

        titulo = request.POST.get('titulo', '').strip()
        fecha_str = request.POST.get('fecha', '').strip()
        plataforma = request.POST.get('plataforma', '').strip()
        formato = request.POST.get('formato', '').strip()
        guion = request.POST.get('guion', '').strip()

        if not titulo or not fecha_str or not plataforma or not formato:
            messages.error(request, 'Título, fecha, plataforma y formato son obligatorios')
            return redirect(request.META.get('HTTP_REFERER', 'marketing'))

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Fecha inválida')
            return redirect(request.META.get('HTTP_REFERER', 'marketing'))

        pub = PublicacionMarketing(
            owner=user,
            titulo=titulo,
            fecha=fecha,
            plataforma=plataforma,
            formato=formato,
            guion=guion
        )
        pub.save()
        messages.success(request, 'Publicación planificada correctamente')
        from django.urls import reverse
        return redirect(reverse('marketing') + f'?week={fecha.strftime("%Y-%m-%d")}')

    return redirect('marketing')


@admin_permission_required('marketing')
def marketing_editar(request, pub_id):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        return HttpResponse('No autorizado', status=401)

    from .models import PublicacionMarketing
    pub = get_object_or_404(PublicacionMarketing, id=pub_id, owner_id=user_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        fecha_str = request.POST.get('fecha', '').strip()
        plataforma = request.POST.get('plataforma', '').strip()
        formato = request.POST.get('formato', '').strip()
        guion = request.POST.get('guion', '').strip()

        if not titulo or not fecha_str or not plataforma or not formato:
            messages.error(request, 'Título, fecha, plataforma y formato son obligatorios')
            return redirect(request.META.get('HTTP_REFERER', 'marketing'))

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Fecha inválida')
            return redirect(request.META.get('HTTP_REFERER', 'marketing'))

        pub.titulo = titulo
        pub.fecha = fecha
        pub.plataforma = plataforma
        pub.formato = formato
        pub.guion = guion
        pub.save()

        messages.success(request, 'Publicación actualizada correctamente')
        from django.urls import reverse
        return redirect(reverse('marketing') + f'?week={fecha.strftime("%Y-%m-%d")}')

    return redirect('marketing')


@admin_permission_required('marketing')
def marketing_eliminar(request, pub_id):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        return HttpResponse('No autorizado', status=401)

    from .models import PublicacionMarketing
    pub = get_object_or_404(PublicacionMarketing, id=pub_id, owner_id=user_id)
    fecha_redirect = pub.fecha.strftime("%Y-%m-%d")
    pub.delete()

    messages.success(request, 'Publicación eliminada correctamente')
    from django.urls import reverse
    return redirect(reverse('marketing') + f'?week={fecha_redirect}')


@admin_permission_required('control_usuarios')
def control_usuarios(request):
    user = _get_session_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        action = request.POST.get('action')
        from django.contrib.auth.hashers import make_password
        
        if action == 'add_user':
            nombre = request.POST.get('nombre', '').strip()
            email = request.POST.get('email', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            password = request.POST.get('password', '').strip()
            bloqueado = request.POST.get('bloqueado') == 'on'
            permisos_list = request.POST.getlist('permisos')

            if not nombre or not password:
                messages.error(request, 'El nombre y la contraseña son obligatorios.')
            elif User_admin.objects.filter(nombre=nombre).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
            else:
                User_admin.objects.create(
                    nombre=nombre,
                    email=email if email else None,
                    telefono=telefono if telefono else None,
                    password=make_password(password),
                    bloqueado=bloqueado,
                    permisos=permisos_list
                )
                messages.success(request, f'Usuario "{nombre}" creado con éxito.')

        elif action == 'edit_user':
            user_id = request.POST.get('user_id')
            nombre = request.POST.get('nombre', '').strip()
            email = request.POST.get('email', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            password = request.POST.get('password', '').strip()
            bloqueado = request.POST.get('bloqueado') == 'on'
            permisos_list = request.POST.getlist('permisos')

            if not nombre:
                messages.error(request, 'El nombre es obligatorio.')
            else:
                try:
                    u = User_admin.objects.get(id=user_id)
                    if User_admin.objects.filter(nombre=nombre).exclude(id=u.id).exists():
                        messages.error(request, 'El nombre de usuario ya está en uso.')
                    else:
                        u.nombre = nombre
                        u.email = email if email else None
                        u.telefono = telefono if telefono else None
                        u.bloqueado = bloqueado
                        u.permisos = permisos_list
                        if password:
                            u.password = make_password(password)
                        u.save()
                        messages.success(request, f'Usuario "{nombre}" actualizado.')
                except User_admin.DoesNotExist:
                    messages.error(request, 'Usuario no encontrado.')

        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            if user_id:
                try:
                    u = User_admin.objects.get(id=user_id)
                    if u.nombre == 'admin' or u.id == user.id:
                        messages.error(request, 'No puedes eliminar al administrador principal o a ti mismo.')
                    else:
                        nombre = u.nombre
                        u.delete()
                        messages.success(request, f'Usuario "{nombre}" eliminado.')
                except User_admin.DoesNotExist:
                    messages.error(request, 'Usuario no encontrado.')

        return redirect('control_usuarios')

    usuarios = User_admin.objects.all().order_by('nombre')
    return render(request, 'usuarios.html', {
        'user': user,
        'usuarios': usuarios
    })

def contactos_web_view(request):
    user = _get_session_user(request)
    if not user:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')

    from app1.models import Contacto
    contactos_web = Contacto.objects.all().order_by('-fecha_creacion')
    
    return render(request, 'contactos_web.html', {'user': user, 'contactos_web': contactos_web})


def control_noticias(request):
    user = _get_session_user(request)
    if not user:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')

    from app1.models import Noticia
    from django.utils.text import slugify

    # Crear noticia
    if request.method == 'POST' and 'crear_noticia' in request.POST:
        titulo = request.POST.get('titulo', '').strip()
        categoria = request.POST.get('categoria', 'Actualidad').strip()
        resumen = request.POST.get('resumen', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        tiempo_lectura = request.POST.get('tiempo_lectura', '3 min').strip()
        foto_url = request.POST.get('foto_url', '').strip()
        destacado = 'destacado' in request.POST
        foto = request.FILES.get('foto')

        if titulo and resumen:
            slug = slugify(titulo)
            base_slug = slug
            counter = 1
            while Noticia.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            Noticia.objects.create(
                titulo=titulo,
                slug=slug,
                categoria=categoria,
                resumen=resumen,
                contenido=contenido,
                tiempo_lectura=tiempo_lectura,
                foto_url=foto_url,
                destacado=destacado,
                foto=foto
            )
            messages.success(request, 'Noticia publicada exitosamente en la web.')
            return redirect('control_noticias')
        else:
            messages.error(request, 'Título y resumen son requeridos.')

    # Editar noticia
    if request.method == 'POST' and 'editar_noticia' in request.POST:
        noticia_id = request.POST.get('noticia_id')
        noticia = get_object_or_404(Noticia, id=noticia_id)
        noticia.titulo = request.POST.get('titulo', noticia.titulo).strip()
        noticia.categoria = request.POST.get('categoria', noticia.categoria).strip()
        noticia.resumen = request.POST.get('resumen', noticia.resumen).strip()
        noticia.contenido = request.POST.get('contenido', noticia.contenido).strip()
        noticia.tiempo_lectura = request.POST.get('tiempo_lectura', noticia.tiempo_lectura).strip()
        noticia.foto_url = request.POST.get('foto_url', noticia.foto_url).strip()
        noticia.destacado = 'destacado' in request.POST
        if 'foto' in request.FILES:
            noticia.foto = request.FILES['foto']
        noticia.save()
        messages.success(request, 'Noticia actualizada correctamente.')
        return redirect('control_noticias')

    noticias = Noticia.objects.all().order_by('-fecha', '-id')
    return render(request, 'control_noticias.html', {
        'user': user,
        'noticias': noticias
    })

def eliminar_noticia_view(request, noticia_id):
    user = _get_session_user(request)
    if not user:
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')

    from app1.models import Noticia
    if request.method == 'POST':
        noticia = get_object_or_404(Noticia, id=noticia_id)
        noticia.delete()
        messages.success(request, 'Noticia eliminada correctamente.')
    return redirect('control_noticias')
