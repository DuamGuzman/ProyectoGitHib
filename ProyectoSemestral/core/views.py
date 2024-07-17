from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .forms import *
from .models import Orden, Producto
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
import os
from django.conf import settings
from django.contrib.staticfiles import finders
from reportlab.lib.units import inch
from django.core.files.storage import FileSystemStorage
from .models import * 
from reportlab.lib.colors import Color, lightgrey, red, darkred




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

    # Si la orden está anulada, agrega la marca de agua en rojo translúcido
    if orden.estado.nombre == 'Anulada':
        p.saveState()
        p.setFont("Helvetica-Bold", 90)  # Aumenta el tamaño de la fuente un 50%
        # Define un color rojo translúcido (RGBA)
        red_translucent = Color(1, 0, 0, alpha=0.5)  # Rojo, sin verde, sin azul, 50% de transparencia
        p.setFillColor(red_translucent)
        p.translate(width/2, height/2)
        p.rotate(45)
        p.drawCentredString(0, 0, "ANULADO")
        p.restoreState()

    # Detalles de la orden
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30, height - 60, "Detalles de la orden")
    p.setFont("Helvetica", 10)
    p.drawString(30, height - 80, f"ID de la orden: {orden.numero_orden}")
    p.drawString(30, height - 100, f"Fecha: {orden.fecha_orden}")
    p.drawString(30, height - 120, f"Tipo de servicio: {orden.tipo_servicio}")

    # Datos del vendedor
    vendedor_y = height - 160
    p.setFont("Helvetica-Bold", 10)
    p.drawString(30, vendedor_y, "Datos del vendedor")
    p.setFont("Helvetica", 10)
    p.drawString(30, vendedor_y - 20, f"Nombre: {orden.razon_social}")
    p.drawString(30, vendedor_y - 40, f"Dirección: {orden.direccion}")
    p.drawString(30, vendedor_y - 60, f"Teléfono: {orden.telefono}")
    p.drawString(30, vendedor_y - 80, f"Correo: {orden.correo}")
    p.drawString(30, vendedor_y - 100, f"Sitio web: {orden.sitio_web}")

    # Datos del cliente
    cliente_y = height - 160
    p.setFont("Helvetica-Bold", 10)
    p.drawString(300, cliente_y, "Datos del cliente")
    p.setFont("Helvetica", 10)
    p.drawString(300, cliente_y - 20, f"RUT: {orden.rut_cliente}")
    p.drawString(300, cliente_y - 40, f"Nombre: {orden.nombre_razon_social}")
    p.drawString(300, cliente_y - 60, f"Dirección: {orden.direccion_cliente}")
    p.drawString(300, cliente_y - 80, f"Teléfono: {orden.telefono_cliente}")
    p.drawString(300, cliente_y - 100, f"Correo: {orden.correo_clinte}")

    # Tabla de productos
    table_y = min(vendedor_y, cliente_y) - 190
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
    table.drawOn(p, 30, table_y)

    # Resumen de la orden
    resumen_y = table_y - 300
    p.setFont("Helvetica-Bold", 10)
    p.drawString(400, resumen_y, "Resumen de la Orden:")
    p.setFont("Helvetica", 10)
    p.drawString(400, resumen_y - 20, f"Precio Unitario con IVA: ${producto.precio_unitario * 1.19:.2f}")

    # Guarda el PDF generado
    p.showPage()
    p.save()
    
    return response


@login_required
def actualizar_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)

    if request.method == 'POST':
        form = OrdenFormActualizar(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            # Cambiar el estado a 'Rectificada'
            estado, created = Estado.objects.get_or_create(orden=orden)
            estado.nombre = 'Rectificada'
            estado.save()
            return redirect('ordenlista')  # Redirigir a la lista de órdenes después de actualizar
    else:
        form = OrdenFormActualizar(instance=orden)

    return render(request, 'core/actualizar_orden.html', {'form': form})


@login_required
def aceptarOrden(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')  # Accede al archivo desde el formulario

        # Puedes hacer validaciones adicionales aquí si es necesario
        # Por ejemplo, verificar el tipo de archivo, tamaño máximo, etc.

        if archivo:
            # Guarda el archivo en el servidor
            fs = FileSystemStorage()
            nombre_archivo = fs.save(archivo.name, archivo)

          

            return redirect('ruta_hacia_la_vista_de_confirmacion')  

    # Si no es una solicitud POST o no hay archivo, simplemente renderiza la página con los datos existentes
    ordenes = Orden.objects.all()
    productos = Producto.objects.all()
    return render(request, 'core/aceptarOrden.html', {'ordenes': ordenes, 'productos': productos})


def detalleorden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    comprobante, created = Comprobante.objects.get_or_create(compra=orden)

    if request.method == 'POST':
        # Guardar datos del cliente
        datos_cliente = request.POST.get('datos_cliente')
        comprobante.datos_cliente = datos_cliente

        # Manejar la subida del archivo
        comprobante_file = request.FILES.get('comprobante_file')
        if comprobante_file:
            comprobante.comprobante = comprobante_file

        comprobante.save()

        # Cambiar el estado del pedido a 'Entregada'
        estado_pedido, created = EstadoPedido.objects.get_or_create(orden=orden)
        estado_pedido.nombre = 'Entregada'
        estado_pedido.save()

        return redirect('ordenlista')

    return render(request, 'core/detalleorden.html', {'orden': orden, 'comprobante': comprobante})

def verdetalle(request, orden_id):
    orden = get_object_or_404(Orden, pk=orden_id)
    comprobante = get_object_or_404(Comprobante, compra=orden)

    return render(request, 'core/verdetalle.html', {'orden': orden, 'comprobante': comprobante})


def rechazar(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    comprobante, created = Comprobante.objects.get_or_create(compra=orden)

    if request.method == 'POST':
        datos_cliente = request.POST.get('datos_cliente')
        action = request.POST.get('action')
        if action == 'rechazar':
            # Guardar los datos del cliente
            comprobante.datos_cliente = datos_cliente
            comprobante.save()
            
            # Cambiar el estado del pedido a 'Rechazada'
            estado_pedido, created = EstadoPedido.objects.get_or_create(orden=orden)
            estado_pedido.nombre = 'Rechazada'
            estado_pedido.save()
        return redirect('ordenlista')  # Redirigir a la lista de órdenes después de la acción

    return render(request, 'core/rechazar.html', {'orden': orden})


def mi_vista(request, orden_id):
    orden = get_object_or_404(Orden, pk=orden_id)
    total_con_iva = sum(producto.precio_unitario * (1 + producto.tasa_iva) for producto in orden.productos.all())
   
    context = {
        'orden': orden,
        'total_con_iva': total_con_iva,
    }
    return render(request, 'ordenlista.html', context)


def anular(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    
    if request.method == 'POST':
        # Obtener o crear la instancia de Estado correspondiente a la orden
        estado, created = Estado.objects.get_or_create(orden=orden)
        estado.nombre = 'Anulada'
        estado.save()
        
        # Redirigir a la lista de órdenes después de actualizar
        return redirect('ordenlista')

    # Renderizar la plantilla anular.html pasando la orden
    return render(request, 'core/anular.html', {'orden': orden})