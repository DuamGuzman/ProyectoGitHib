from django.contrib import admin

from .models import *

# Register your models here.


admin.site.register(Orden)
admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(Estado)
admin.site.register(EstadoPedido)
admin.site.register(Comprobante)