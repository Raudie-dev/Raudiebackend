from app1.models import Prueba, Servicios, Proyecto

# Nuevas funciones: CRUD para Proyecto
def crear_prueba(nombre, fecha, socio=True):
    return Prueba.objects.create(nombre=nombre, fecha=fecha, socio=socio)

def obtener_pruebas():
    return Prueba.objects.all()

def eliminar_prueba(prueba_id):
    Prueba.objects.filter(id=prueba_id).delete()

def actualizar_prueba(prueba_id, nombre=None, fecha=None, socio=None):
    prueba = Prueba.objects.get(id=prueba_id)
    if nombre is not None:
        prueba.nombre = nombre
    if fecha is not None:
        prueba.fecha = fecha
    if socio is not None:
        prueba.socio = socio
    prueba.save()
    return prueba


def crear_servicio(nombre, titulo, precio, descripcion, caracteristicas=None, foto=None):
    if caracteristicas is None:
        caracteristicas = []
    servicio = Servicios(
        nombre=nombre,
        titulo=titulo,
        precio=precio,
        descripcion=descripcion,
        caracteristicas=caracteristicas
    )
    if foto:
        servicio.foto = foto
    servicio.save()
    return servicio

def obtener_servicios():
    return Servicios.objects.all().order_by('-id')

def eliminar_servicio(servicio_id):
    Servicios.objects.filter(id=servicio_id).delete()

def actualizar_servicio(servicio_id, nombre=None, titulo=None, precio=None, descripcion=None, caracteristicas=None, foto=None):
    servicio = Servicios.objects.get(id=servicio_id)
    if nombre is not None:
        servicio.nombre = nombre
    if titulo is not None:
        servicio.titulo = titulo
    if precio is not None:
        servicio.precio = precio
    if descripcion is not None:
        servicio.descripcion = descripcion
    if caracteristicas is not None:
        servicio.caracteristicas = caracteristicas
    if foto is not None:
        servicio.foto = foto
    servicio.save()
    return servicio

# Nuevas funciones: CRUD para Proyecto
def crear_proyecto(titulo, cliente, fecha, descripcion='', caracteristicas=None, fotos=None, categoria_ids=None, tecnologia_ids=None):
    if caracteristicas is None:
        caracteristicas = []
    if fotos is None:
        fotos = []
    if categoria_ids is None:
        categoria_ids = []
    if tecnologia_ids is None:
        tecnologia_ids = []

    proyecto = Proyecto(
        titulo=titulo,
        cliente=cliente,
        fecha=fecha,
        descripcion=descripcion,
        caracteristicas=caracteristicas,
        fotos=fotos
    )
    proyecto.save()
    # asignar M2M si se proporcionaron ids
    if categoria_ids is not None:
        proyecto.categorias.set(categoria_ids)
    if tecnologia_ids is not None:
        proyecto.tecnologias.set(tecnologia_ids)
    return proyecto

def obtener_proyectos():
    return Proyecto.objects.all().order_by('-fecha', '-id')

def eliminar_proyecto(proyecto_id):
    Proyecto.objects.filter(id=proyecto_id).delete()

def actualizar_proyecto(proyecto_id, titulo=None, cliente=None, fecha=None, descripcion=None, caracteristicas=None, fotos=None, categoria_ids=None, tecnologia_ids=None):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    if titulo is not None:
        proyecto.titulo = titulo
    if cliente is not None:
        proyecto.cliente = cliente
    if fecha is not None:
        proyecto.fecha = fecha
    if descripcion is not None:
        proyecto.descripcion = descripcion
    if caracteristicas is not None:
        proyecto.caracteristicas = caracteristicas
    if fotos is not None:
        proyecto.fotos = fotos
    proyecto.save()
    # actualizar relaciones M2M (None = no tocar, [] = limpiar)
    if categoria_ids is not None:
        proyecto.categorias.set(categoria_ids)
    if tecnologia_ids is not None:
        proyecto.tecnologias.set(tecnologia_ids)
    return proyecto