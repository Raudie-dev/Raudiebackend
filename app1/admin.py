from django.contrib import admin
from .models import Contacto, Proyecto, Servicios, Categoria, Tecnologia, Noticia

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'whatsapp', 'email', 'fecha_creacion')
    search_fields = ('nombre', 'whatsapp', 'email')
    readonly_fields = ('fecha_creacion',)

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'fecha')
    search_fields = ('titulo', 'cliente', 'descripcion')
    filter_horizontal = ('categorias', 'tecnologias')

@admin.register(Servicios)
class ServiciosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre', 'descripcion')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Tecnologia)
class TecnologiaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha', 'tiempo_lectura', 'destacado')
    list_filter = ('categoria', 'destacado', 'fecha')
    search_fields = ('titulo', 'resumen', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}
