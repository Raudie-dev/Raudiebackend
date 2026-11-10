from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os
import shutil

# Auto-sync assets -> static (STATIC_ROOT) and official services to DB on startup
try:
    assets_dir = os.path.join(settings.BASE_DIR, 'assets')
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root and os.path.isdir(assets_dir):
        shutil.copytree(assets_dir, static_root, dirs_exist_ok=True)
except Exception:
    pass

try:
    from app1.services_data import sync_servicios_to_db
    sync_servicios_to_db()
except Exception:
    pass

urlpatterns = [
    path('', include('app1.urls')),
    path('app2/', include('app2.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
