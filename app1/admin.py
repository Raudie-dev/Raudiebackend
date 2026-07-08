from django.contrib import admin
from .models import Contacto

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'whatsapp', 'email', 'fecha_creacion')
    search_fields = ('nombre', 'whatsapp', 'email')
    readonly_fields = ('fecha_creacion',)
