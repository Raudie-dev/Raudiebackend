from django.db import models

class Prueba(models.Model):
    nombre = models.CharField(max_length=200)
    fecha = models.DateField()
    socio = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Servicios(models.Model):
    nombre = models.CharField(max_length=200)
    titulo = models.CharField(max_length=200, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()

    caracteristicas = models.JSONField(default=list, blank=True)
    foto = models.ImageField(upload_to='servicios/', blank=True, null=True)

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombre

class Tecnologia(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    titulo = models.CharField(max_length=200)
    cliente = models.CharField(max_length=200, blank=True)
    fecha = models.DateField()
    descripcion = models.TextField(blank=True)
    caracteristicas = models.JSONField(default=list, blank=True)
    fotos = models.JSONField(default=list, blank=True)
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='proyectos')
    tecnologias = models.ManyToManyField(Tecnologia, blank=True, related_name='proyectos')

    def fotos_lista(self):
        return self.fotos or []

    def __str__(self):
        return self.titulo if self.titulo else f"Proyecto {self.pk}"