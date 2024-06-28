from django.db import models 
from django.core.validators import MinValueValidator
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
    
class Producto(models.Model):
    codigo_producto = models.CharField(max_length=200)
    nombre_producto = models.CharField(max_length=200)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.nombre_producto

class Orden(models.Model):
    numero_orden = models.CharField(max_length=10)
    fecha_orden = models.CharField(max_length=10)
    productos = models.ManyToManyField('Producto')  # Cambiado a ManyToManyField
    rut_cliente = models.CharField(max_length=12)
    nombre_razon_social = models.CharField(max_length=100)
    direccion_cliente = models.CharField(max_length=200)
    telefono_cliente = models.CharField(max_length=15)
    correo_clinte = models.EmailField()
    rut = models.CharField(max_length=12, blank=True, null=True)
    razon_social = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    sitio_web = models.URLField(blank=True, null=True)
    tipo_servicio = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        super().clean()
        try:
            fecha_orden_datetime = datetime.datetime.strptime(self.fecha_orden, '%d/%m/%Y')
        except ValueError:
            raise ValidationError('El formato de la fecha debe ser DD/MM/YYYY.')

        # Hacer aware la fecha de la orden
        fecha_orden_datetime = timezone.make_aware(fecha_orden_datetime, timezone.get_current_timezone())
        
        if fecha_orden_datetime > timezone.now():
            raise ValidationError('La fecha de la orden no puede ser mayor a la fecha actual.')

    def __str__(self):
        return self.numero_orden

class Usuario(models.Model):
    nombreUsuario = models.CharField(max_length=200,blank=False,null=False )
    contrasenaUsuario = models.CharField(max_length=200,blank=False,null=False)

    def __str__(self):
        return self.nombreUsuario
