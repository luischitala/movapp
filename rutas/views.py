# Vistas de rutas
# Imports de Django
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files import File
# Imports para el proyecto
import os
import xlrd
import pandas as pd
#Importando librerias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import time
from sklearn.cluster import MiniBatchKMeans, KMeans





# Create your views here.
def inicio(request):
    # Inicio sesión
    return render(request, 'rutas/inicio.html')


def ruta(request):

    
    return render(request, 'rutas/rutas.html')
   
  


def test(request):
    longitude = float(request.POST.get('lnging'))
    latitude = float(request.POST.get('lating'))
    coords = {"latitude":latitude,"longitude":longitude}
    print(coords)

    #Inicializacion de variables de tu posicion
    my_latitude = latitude
    my_longitude = longitude
    my_location = (my_latitude, my_longitude)
    np_my_location_arr = np.array([my_latitude,my_longitude])
    df_my_location = pd.DataFrame({'Latitud': [my_latitude],'Longitud': [my_longitude]})
   
    #Importando los datos y convirtiendolo en un dataframe
    

    df_Hospitals = pd.read_excel('')
        



    return  HttpResponse('Las coordenadas ingresadas fueron:')



