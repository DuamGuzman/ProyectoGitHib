from django.urls import path
from .views import *

urlpatterns = [
    path('index/', index, name="index"),
    path('orden/', orden, name='orden'),
    path('', login, name='login'),
    path('producto/', producto, name='producto'),
    path('ordenlista/', ordenlista, name='ordenlista'),


    
]