from django.db import models
from django.utils.text import slugify

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

    @property
    def slug(self):
        return slugify(self.nombre) or f'servicio-{self.pk}'

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

    @property
    def slug(self):
        return slugify(self.titulo or '') or f'proyecto-{self.pk or 1}'

    def fotos_lista(self):
        return self.fotos or []

    def __str__(self):
        return self.titulo if self.titulo else f"Proyecto {self.pk}"

class Contacto(models.Model):
    nombre = models.CharField(max_length=200)
    whatsapp = models.CharField(max_length=50)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.whatsapp}"

class Noticia(models.Model):
    titulo = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    categoria = models.CharField(max_length=100, default='Actualidad')
    resumen = models.TextField()
    contenido = models.TextField(blank=True)
    fecha = models.DateField(auto_now_add=True)
    foto = models.ImageField(upload_to='noticias/', blank=True, null=True)
    foto_url = models.URLField(blank=True, help_text='URL de imagen externa')
    tiempo_lectura = models.CharField(max_length=50, default='3 min')
    destacado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'
        ordering = ['-fecha', '-id']

    @property
    def url_slug(self):
        return self.slug or slugify(self.titulo) or f'noticia-{self.pk}'

    def __str__(self):
        return self.titulo
