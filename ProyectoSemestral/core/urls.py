from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('index/', index, name="index"),
    path('orden/', orden, name='orden'),
    path('', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('producto/', producto, name='producto'),
    path('ordenlista/', ordenlista, name='ordenlista'),
     path('ordenlista/<int:orden_id>/descargar-pdf/', views.descargar_pdf, name='descargar_pdf'),

    
]