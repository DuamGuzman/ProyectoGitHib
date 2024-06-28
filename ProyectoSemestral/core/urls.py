from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('index/', index, name="index"),
    path('orden/', orden, name='orden'),
    path('', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('producto/', producto, name='producto'),
    path('ordenlista/', ordenlista, name='ordenlista'),


    
]