from django import forms
from .models import Orden, Producto

class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden 
        fields = '__all__'


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
