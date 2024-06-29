from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .forms import OrdenForm, ProductoForm
from .models import Orden, Producto
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
import os
from django.conf import settings
from django.contrib.staticfiles import finders
from reportlab.lib.units import inch
# Create your views here.
@login_required
def index(request):
    return render(request, 'core/index.html')

@login_required
def ordenlista(request):
    ordenes = Orden.objects.all()
    productos = Producto.objects.all()
    return render(request, 'core/ordenlista.html',{'ordenes': ordenes,'productos': productos})


from django.shortcuts import redirect

@login_required
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

@login_required
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

@login_required
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

def descargar_pdf(request, orden_id):
    # Obtén la orden específica según el orden_id
    orden = get_object_or_404(Orden, pk=orden_id)

    # Calcula el subtotal sumando el precio total de cada producto en la orden
    productos_orden = orden.productos.all()
    subtotal = sum(producto.precio_unitario * orden.cantidad for producto in productos_orden)
    
    # Calcula el IVA y el total
    iva = subtotal * 0.19
    total = subtotal + iva

    # Inicializa el objeto de lienzo para el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orden_compra_{orden.numero_orden}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    p.setFont("Helvetica", 12)

    # Título del documento
    p.setFont("Helvetica-Bold", 18)
    p.drawString(200, height - 40, "ORDEN DE COMPRA")
    
    # Datos del vendedor
    p.setFont("Helvetica-Bold", 10)
    p.drawString(30, height - 80, "Datos del vendedor")
    p.setFont("Helvetica", 10)
    p.drawString(30, height - 100, f"Nombre: {orden.razon_social}")
    p.drawString(30, height - 120, f"Dirección: {orden.direccion}")
    p.drawString(30, height - 140, f"Teléfono: {orden.telefono}")
    p.drawString(30, height - 160, f"Correo: {orden.correo}")
    p.drawString(30, height - 180, f"Sitio web: {orden.sitio_web}")

    # Datos del cliente
    p.setFont("Helvetica-Bold", 10)
    p.drawString(300, height - 80, "Datos del cliente")
    p.setFont("Helvetica", 10)
    p.drawString(300, height - 100, f"Nombre: {orden.nombre_razon_social}")
    p.drawString(300, height - 120, f"Dirección: {orden.direccion_cliente}")
    p.drawString(300, height - 140, f"Teléfono: {orden.telefono_cliente}")
    p.drawString(300, height - 160, f"Correo: {orden.correo_clinte}")

    # Tabla de productos
    data = [["Artículo", "Descripción", "Unidades", "Precio Unidad", "Total"]]
    for i, producto in enumerate(productos_orden, start=1):
        data.append([i, producto.nombre_producto, orden.cantidad, f"${producto.precio_unitario:.2f}", f"${producto.precio_unitario * orden.cantidad:.2f}"])
    
    table = Table(data, colWidths=[50, 200, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height - 300)

    # Resumen de la orden
    p.setFont("Helvetica-Bold", 10)
    p.drawString(400, 180, "Resumen de la Orden:")
    p.setFont("Helvetica", 10)
    p.drawString(400, 160, f"Subtotal: ${subtotal:.2f}")
    p.drawString(400, 140, f"IVA: ${iva:.2f}")
    p.drawString(400, 120, f"Total: ${total:.2f}")

    # Guarda el PDF generado
    p.showPage()
    p.save()
    
    return response
