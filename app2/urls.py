from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('control_servicios/', views.control_servicios, name='control_servicios'),
    path('control_proyectos/', views.control_proyectos, name='control_proyectos'),
]