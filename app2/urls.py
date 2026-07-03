from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('control_servicios/', views.control_servicios, name='control_servicios'),
    path('control_proyectos/', views.control_proyectos, name='control_proyectos'),
    # path('solicitudes_cotizacion/', views.solicitudes_cotizacion, name='solicitudes_cotizacion'),
    path('logout/', views.logout, name='logout'),

    # Bot views
    path('bot/estado/', views.estado, name='estado'),
    path('bot/configuracion/', views.configuracion, name='configuracion'),
    path('bot/telegram/', views.telegram_configuracion, name='telegram_configuracion'),
    path('bot/delete/<int:bot_id>/', views.delete_bot, name='delete_bot'),
    path('bot/create_edit/<int:bot_id>/', views.create_edit_bot, name='create_edit_bot'),
    path('bot/enviar_reclamo/', views.enviar_reclamo, name='enviar_reclamo'),
    path('bot/chat/', views.public_chat, name='public_chat'),
    path('bot/telegram_webhook/<int:bot_id>/', views.telegram_webhook, name='telegram_webhook'),
    path('bot/send_message/', views.send_message, name='send_message'),
    path('bot/reset_chat/', views.reset_chat, name='reset_chat'),
    path('bot/panel_control/', views.estado, name='panel_control'),  # Alias for redirection

    # Departamentos
    path('bot/departamentos/', views.departamentos, name='departamentos'),
    path('bot/departamentos/crear/', views.departamento_crear, name='departamento_crear'),
    path('bot/departamentos/editar/<int:dpto_id>/', views.departamento_editar, name='departamento_editar'),
    path('bot/departamentos/eliminar/<int:dpto_id>/', views.departamento_eliminar, name='departamento_eliminar'),

    # Agentes
    path('bot/agentes/', views.agentes, name='agentes'),
    path('bot/agentes/crear/', views.agente_crear, name='agente_crear'),
    path('bot/agentes/editar/<int:agente_id>/', views.agente_editar, name='agente_editar'),
    path('bot/agentes/eliminar/<int:agente_id>/', views.agente_eliminar, name='agente_eliminar'),

    # Conversaciones y Cola
    path('bot/conversaciones/', views.conversaciones, name='conversaciones'),
    path('bot/conversaciones/<str:remote_jid>/', views.conversacion_detalle, name='conversacion_detalle'),
    path('bot/perfil/', views.perfil, name='perfil'),
    path('bot/queue/drain/', views.queue_drain, name='queue_drain'),
    path('bot/queue/status/', views.queue_status, name='queue_status'),

    # Contabilidad y Presupuestos
    path('contabilidad/costos/', views.contabilidad_costos, name='contabilidad_costos'),
    path('contabilidad/finanzas/', views.contabilidad_finanzas, name='contabilidad_finanzas'),
    path('contabilidad/cotizacion/', views.generar_cotizacion, name='generar_cotizacion'),

    # Marketing
    path('marketing/', views.marketing_view, name='marketing'),
    path('marketing/crear/', views.marketing_crear, name='marketing_crear'),
    path('marketing/editar/<int:pub_id>/', views.marketing_editar, name='marketing_editar'),
    path('marketing/eliminar/<int:pub_id>/', views.marketing_eliminar, name='marketing_eliminar'),

    # Usuarios
    path('usuarios/', views.control_usuarios, name='control_usuarios'),
]