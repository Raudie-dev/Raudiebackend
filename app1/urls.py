from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('servicios/<int:servicio_id>/', views.servicios_detalle, name='servicio_detalle'),
    path('enlaces/', views.enlaces, name='enlaces'),
    path('proyectos/', views.proyectos, name='proyectos'),
    path('proyectos/<int:proyecto_id>/', views.proyecto_detalle, name='proyecto_detalle'),
    path('noticias/', views.noticias, name='noticias'),
    path('noticias/<int:noticia_id>/', views.noticia_detalle, name='noticia_detalle'),
    path('guardar-contacto/', views.guardar_contacto, name='guardar_contacto'),
]
