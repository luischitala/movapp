
from django.contrib import admin
from django.urls import path
from django.config import settings 
from django.config.urls.static import static

from movapp import views as local_views
from rutas import views as rutas_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', local_views.hello_world),

    path('', rutas_views.inicio),
    path('ruta/', rutas_views.ruta),
    path('ruta/resultado', rutas_views.resultado),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

