from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('orden/', views.orden, name='orden'),
    path('', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('producto/', views.producto, name='producto'),
    path('ordenlista/', views.ordenlista, name='ordenlista'),
    path('ordenlista/<int:orden_id>/descargar-pdf/', views.descargar_pdf, name='descargar_pdf'),
    path('actualizar_orden/<int:orden_id>/', views.actualizar_orden, name='actualizar_orden'),
    path('aceptarOrden/', views.aceptarOrden, name='aceptarOrden'),
    path('detalleorden/<int:orden_id>/', views.detalleorden, name='detalleorden'),
    path('verdetalle/<int:orden_id>/', views.verdetalle, name='verdetalle'),
    path('rechazar/<int:orden_id>/', views.rechazar, name='rechazar'),
    path('orden/<int:id_orden>/', views.mi_vista, name='detalle_orden'),  # Ajusta la vista si es necesario
    path('anular/<int:orden_id>/', views.anular, name='anular'),
]