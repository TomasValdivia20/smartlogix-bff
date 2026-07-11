from django.contrib import admin
from django.urls import path
from app_web_api.api import api
from app_web_api.views_pdf import descargar_guia_pdf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/pedidos/<uuid:pedido_id>/guia/pdf', descargar_guia_pdf, name='guia-pdf'),
    path('api/', api.urls),
]
