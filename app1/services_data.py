"""
services_data.py
Definición centralizada en código de los servicios oficiales de RauDie Web Developers.
Los servicios son gestionados exclusivamente en código fuente para garantizar coherencia
de diseño editorial, estructura técnica y SEO (no modificables desde el panel).
"""

from typing import List, Dict, Any, Optional

SERVICIOS_DATA: List[Dict[str, Any]] = [
    {
        "id": 1,
        "slug": "landing-page-basica",
        "nombre": "Landing Page Básica",
        "badge": "Plan Esencial",
        "icono": "fas fa-laptop-code",
        "titulo": "La mejor opción para empezar con presencia sólida",
        "descripcion": (
            "Una Landing Page Básica es un sitio web de una sola sección diseñado estratégicamente "
            "para presentar la información esencial de tu negocio o servicio. Es ideal para pequeños "
            "emprendimientos, profesionales independientes o para promocionar un producto o evento "
            "específico con carga ultrarrápida y alta conversión."
        ),
        "precio": 200.0,
        "precio_display": "$200 USD",
        "bonus": "INCLUYE HOSTING Y DOMINIO POR 1 AÑO",
        "caracteristicas": [
            "Diseño de sección de alto impacto",
            "Integración con redes sociales",
            "Optimización de velocidad de recarga",
            "Formulario de contacto integrado",
            "Diseño adaptado para móviles",
            "Optimización de SEO básica para buscadores",
        ],
    },
    {
        "id": 2,
        "slug": "landing-page-pro",
        "nombre": "Landing Page PRO",
        "badge": "Todo lo del Básico +",
        "icono": "fas fa-rocket",
        "titulo": "Estructura multisección y persuasión orientada a ventas",
        "descripcion": (
            "Diseñada para marcas y empresas que buscan transmitir máxima autoridad y confianza. "
            "Incorpora una arquitectura multisección completa (sobre nosotros, catálogo o servicios, "
            "testimonios y preguntas frecuentes), copywriting persuasivo especializado en cerrar clientes, "
            "animaciones interactivas de vanguardia y posicionamiento SEO reforzado."
        ),
        "precio": 350.0,
        "precio_display": "$350 USD",
        "bonus": "INCLUYE HOSTING Y DOMINIO POR 1 AÑO",
        "caracteristicas": [
            "Todo lo del plan Básico incluido",
            "Estructura multisección (sobre nosotros, servicios...)",
            "Copywriting persuasivo enfocado en ventas",
            "Optimización SEO para buscadores",
            "Animaciones y efectos visuales avanzados",
        ],
    },
    {
        "id": 3,
        "slug": "pagina-presentacion-biolink",
        "nombre": "Página de Presentación Bio-link",
        "badge": "Estilo Linktree Pro",
        "icono": "fas fa-link",
        "titulo": "Tu identidad digital y enlaces en un solo destino inteligente",
        "descripcion": (
            "Centraliza todos tus canales de contacto, redes sociales, servicios y enlaces destacados "
            "en una interfaz ligera, moderna y 100% personalizada con la identidad visual de tu marca. "
            "Instalada directamente en tu propio dominio para proyectar profesionalismo sin depender "
            "de plataformas de terceros."
        ),
        "precio": 120.0,
        "precio_display": "$120 USD",
        "bonus": "INSTALACIÓN RÁPIDA EN DOMINIO PROPIO",
        "caracteristicas": [
            "Diseño personalizado estilo Linktree",
            "Botones directos a WhatsApp y redes sociales",
            "Enlaces a servicios o productos destacados",
            "Instalación rápida en tu dominio propio",
        ],
    },
    {
        "id": 4,
        "slug": "ecommerce",
        "nombre": "E-commerce",
        "badge": "Tienda Online Completa",
        "icono": "fas fa-shopping-bag",
        "titulo": "Plataforma de ventas online con pasarela de pagos integrada",
        "descripcion": (
            "Tu tienda virtual lista para procesar cobros y gestionar pedidos las 24 horas. "
            "Cuenta con pasarela de pagos personalizada, sistema de administración de catálogo e inventario "
            "autogestionable, filtros avanzados de búsqueda y notificaciones por correo transaccional."
        ),
        "precio": 600.0,
        "precio_display": "$600 USD",
        "bonus": "INCLUYE HOSTING Y DOMINIO POR 1 AÑO (Aplican ciertas condiciones)",
        "caracteristicas": [
            "Pasarela de pagos personalizadas",
            "Sistema de gestión de inventario y pedidos",
            "Panel de administración autogestionable",
            "Filtros avanzados y buscador de productos",
            "Configuración de correos transaccionales",
        ],
    },
    {
        "id": 5,
        "slug": "invitaciones-digitales",
        "nombre": "Invitaciones Digitales",
        "badge": "Eventos & Celebraciones",
        "icono": "fas fa-envelope-open-text",
        "titulo": "Invitaciones interactivas memorables para ocasiones especiales",
        "descripcion": (
            "Una experiencia web interactiva para compartir con tus invitados por WhatsApp y redes. "
            "Incluye confirmación de asistencia en tiempo real, mapas interactivos con ubicación GPS, "
            "cuenta regresiva dinámica, cronograma detallado del evento y formato optimizado para móviles."
        ),
        "precio": 150.0,
        "precio_display": "$150 USD",
        "bonus": "INCLUYE HOSTING Y DOMINIO POR 1 AÑO",
        "caracteristicas": [
            "Diseño temático personalizado",
            "Confirmación de asistencia vía WhatsApp",
            "Mapa interactivo con ubicación del evento",
            "Contador regresivo y agenda del día",
            "Formato optimizado para compartir en redes",
        ],
    },
    {
        "id": 6,
        "slug": "servicios-personalizados",
        "nombre": "Servicios Personalizados",
        "badge": "A Medida / Custom",
        "icono": "fas fa-cubes",
        "titulo": "Desarrollo de software y soluciones a medida para proyectos exigentes",
        "descripcion": (
            "Diseñamos y desarrollamos soluciones digitales a medida desde cero para satisfacer las "
            "necesidades específicas de tu negocio: plataformas SaaS, sistemas web de gestión interna, "
            "portales corporativos, automatizaciones y conexiones avanzadas con APIs externas. "
            "Ingeniería de software robusta, escalable y con propiedad 100% tuya."
        ),
        "precio": None,
        "precio_display": "A medida",
        "bonus": "CONSULTORÍA Y ARQUITECTURA TÉCNICA INICIAL INCLUIDA",
        "caracteristicas": [
            "Levantamiento de requerimientos y consultoría técnica personalizada",
            "Arquitectura de software escalable, modular y sin ataduras",
            "Integración de bases de datos, APIs de terceros y pasarelas a medida",
            "Diseño de interfaz UI/UX exclusivo con enfoque en usabilidad",
            "Pruebas de calidad (QA), despliegue en la nube y soporte continuo",
        ],
    },
]


def get_servicios() -> List[Dict[str, Any]]:
    """Retorna la lista completa de servicios definidos en código."""
    return SERVICIOS_DATA


def get_servicio_by_id(servicio_id: int) -> Optional[Dict[str, Any]]:
    """Busca un servicio por su ID numérico."""
    for s in SERVICIOS_DATA:
        if s["id"] == int(servicio_id):
            return s
    return None


def get_servicio_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Busca un servicio por su slug textual."""
    for s in SERVICIOS_DATA:
        if s["slug"] == slug:
            return s
    return None


def get_otros_servicios(servicio_id: int, limit: int = 3) -> List[Dict[str, Any]]:
    """Retorna otros servicios excluyendo el actual."""
    return [s for s in SERVICIOS_DATA if s["id"] != int(servicio_id)][:limit]
