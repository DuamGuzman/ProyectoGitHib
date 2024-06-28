from django.shortcuts import render, redirect
from .forms import * # Importar el formulario de productos
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import *
from django.db.models import F, Sum
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def ordenlista(request):
    ordenes = Orden.objects.all()
    productos = Producto.objects.all()
    return render(request, 'core/ordenlista.html',{'ordenes': ordenes,'productos': productos})


from django.shortcuts import redirect

def login_views(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Contraseña válida, iniciar sesión
            login(request, user)
            return redirect('index')  # Redirige al usuario a la página de inicio
        else:
            # Contraseña incorrecta, mostrar mensaje de error
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            return redirect('login')  # Redirige de nuevo al formulario de inicio de sesión

    return render(request, 'core/login.html')


def orden(request):
    
    if request.method == 'POST':
        formulario_orden = OrdenForm(request.POST)

        if formulario_orden.is_valid():
            orden = formulario_orden.save(commit=False)
            orden.save()  # Guardar la orden para obtener un ID
            
            # Obtener los productos asociados a la orden
            productos_orden = orden.productos.all()
            
            
            
            # Calcular el subtotal sumando el precio total de cada producto
            subtotal = sum(producto.precio_unitario * producto.cantidad for producto in productos_orden)
            
            # Calcular el IVA y el total
            iva = subtotal * 0.19
            total = subtotal + iva


            orden.subtotal = subtotal
            orden.iva = iva
            orden.total = total

            orden.save()  # Guardar la orden nuevamente con los valores actualizados
            formulario_orden.save_m2m()

            messages.success(request, "Orden creada correctamente")
            return redirect('index')  
        else:
            messages.error(request, "Error al crear la orden")

    else:
        formulario_orden = OrdenForm()

    aux = {
        'form': formulario_orden,
        'productos': 'productos'
    }
    return render(request, 'core/orden.html', aux)




def login(request):
    return render(request, 'core/login.html')

def producto(request):
    if request.method == 'POST':
        formularioproducto = ProductoForm(request.POST)

        if formularioproducto.is_valid():
            # Asigna los IDs al formulario de orden
            formularioproducto.save()

            messages.success(request, "Producto creado correctamente")
            return redirect('producto')  
        else:
            messages.error(request, "Error al crear la orden")

    else:
        formularioproducto = ProductoForm()

    aux = {
        'form': formularioproducto,
        'msj': ''  # Inicializa la variable 'msj' con un valor vacío
    }
    return render(request, 'core/producto.html', aux)

