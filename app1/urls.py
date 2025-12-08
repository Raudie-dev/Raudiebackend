from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('servicios/<int:servicio_id>/', views.servicios_detalle, name='servicio_detalle'),
    path('enlaces/', views.enlaces, name='enlaces'),
    path('proyectos/', views.proyectos, name='proyectos'),
]