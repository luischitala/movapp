
from django.contrib import admin
from django.urls import path

from movapp import views as local_views
from rutas import views as rutas_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', local_views.hello_world),

    path('', rutas_views.inicio),
    path('ruta/', rutas_views.ruta),
    path('ruta/test', rutas_views.test),
]

