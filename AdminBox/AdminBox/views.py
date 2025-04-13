from django.http import HttpResponse
from django.shortcuts import render
import datetime
from django.template import Template, Context
from django.shortcuts import render
from django.template.loader import get_template


def paginaLogin(request):
    return render(request, 'index.html')

def categoriaEdad(request, edad):
    if edad >= 18:
        if edad >=60:
            categoria = "Tercera Edad"
        else:
            categoria = "Adulto"
    else:
        categoria = "Adolecente"
    resultado = "<h1>Categoría de la edad: %s</h1>" %categoria
    return HttpResponse(resultado)

def obtenerFechaActual(request):
    respuesta = "<h1>Fecha Actual: {0}</h1>".format(datetime.datetime.now().strftime("%d/%m/%Y"))
    return HttpResponse(respuesta)

def plantillaForm(request):
    plantillaExterna = get_template('formulario.html')
    contexto = Context()
    documento = plantillaExterna.render()
    return HttpResponse(documento)

def plantillaShortcut(request):
    return render(request, 'formulario.html')

def plantillaHija(request):
    return render(request, 'plantillaHija.html',{})

def paginaInicio(request):
    return render(request, 'paginaInicio.html')