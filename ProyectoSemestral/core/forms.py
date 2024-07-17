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

class OrdenFormActualizar(forms.ModelForm):
    class Meta:
        model = Orden
        fields = '__all__'  # Incluir todos los campos del modelo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['numero_orden'].disabled = True  # Hacer el campo numero_orden no editable
