# Vistas de rutas
# Imports de Django
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files import File
# Imports para el proyecto
from django.db import models
from rutas.models import Hospital
import os
import xlrd
import pandas as pd
#Importando librerias
import django_pandas as dpd
from django_pandas.io import read_frame
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import time
from sklearn.cluster import MiniBatchKMeans, KMeans
from . import pybingmaps
bing = pybingmaps.Bing('AizoCiuRwxjT9SjxftwCItVoRXI2v0V3UnLTKSebigC5GUW5NklrIZpL5jRANFuJ')
# Visualización Geojson
from geojson import Feature, FeatureCollection, Point
import json





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
     
    qs = Hospital.objects.all()
    df_Hospitals = read_frame(qs)
    # Se eliminó un print hospitals
    df_Hospitals = pd.DataFrame(df_Hospitals)

    #Juntando los datos de las localizaciones del hospital que nutren al algoritmo de Kmeans
    df_LatitudHospitals = pd.DataFrame(df_Hospitals['LATITUD'])
    df_LongitudHospitals = pd.DataFrame(df_Hospitals['LONGITUD'])
    df_coordenadasHospitals = df_LatitudHospitals.join(df_LongitudHospitals)
    # Elminación de print del df
    #Se ejecutara 2 veces, la primera vez el algoritmo para conseguir los centros y la segunda vez para incluir la posicion
    #en la que nos encontramos como un centro
    k_means1 = KMeans(init='k-means++', n_clusters=10, n_init=10)
    k_means1.fit(df_coordenadasHospitals)
    y_kmeans1 = k_means1.predict(df_coordenadasHospitals)
    centers = k_means1.cluster_centers_
    print(centers)
    newcenters = np.insert(centers, 0, np_my_location_arr, axis=0)
    print(newcenters)
    # Definición de nuevos centroides
    newcenters = np.insert(centers, 0, np_my_location_arr, axis=0)
    newcenters
    # 
    k_means2 = KMeans(init=newcenters, n_clusters=11, n_init=1)
    k_means2.fit(df_coordenadasHospitals)
    y_kmeans2 = k_means2.predict(df_coordenadasHospitals)
    # Resultados de Kmeans
    df_Outputs_KMeans = pd.DataFrame(df_Hospitals['NOMBRE_DE_LA_UNIDAD'])
    df_Outputs_KMeans = df_Outputs_KMeans.join(pd.DataFrame(df_Hospitals['LATITUD']))
    df_Outputs_KMeans = df_Outputs_KMeans.join(pd.DataFrame(df_Hospitals['LONGITUD']))
    df_Outputs_KMeans = df_Outputs_KMeans.join(pd.DataFrame(data=y_kmeans2, columns=["Center_Index"]))
   
    # Predicción 
    closest_cluster_center = k_means2.predict(df_my_location)
    # 
    LocateCenters = df_Outputs_KMeans.loc[df_Outputs_KMeans["Center_Index"] == closest_cluster_center[0]] 
    LocateCenters = LocateCenters.reset_index()
    LocateCenters = LocateCenters.drop(['index'], axis=1)
    LocateCenters = LocateCenters.drop(['Center_Index'], axis=1)
    # 
    for i in LocateCenters.index:
        hospital_location = (LocateCenters.iat[i,1], LocateCenters.iat[i,2])
        LocateCenters.at[i, 'Tiempo_Estimado(seg)'] = bing.travelTime(my_location, hospital_location )
        LocateCenters.at[i, 'Distancia_Estimada(km)'] = bing.travelDistance(my_location, hospital_location)
    # Evaluación de parámetros
    Hospitals_nearby_me = LocateCenters
    # Hospitals_nearby_me = LocateCenters.drop(['LATITUD'], axis=1)
    # Hospitals_nearby_me = Hospitals_nearby_me.drop(['LONGITUD'], axis=1)
    Hospitals_nearby_me = Hospitals_nearby_me.join(pd.DataFrame(df_Hospitals['TOTAL_DE_CONSULTORIOS']))
    Hospitals_nearby_me = Hospitals_nearby_me.join(pd.DataFrame(df_Hospitals['TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS']))
    Hospitals_nearby_me
    #Preferencias Funcion de Evaluacion
    #30% Tiempo de Traslado
    #10% Distancia de Traslado
    #10% Cantidad de Consultorios
    #20% Cantidad de Medicos
    #30% Ocupacion

    Evaluacion_Hospitals_nearby_me = Hospitals_nearby_me
    Evaluacion_Hospitals_nearby_me['Ev_Tiempo'] = Hospitals_nearby_me.reset_index() \
                                                    [['Tiempo_Estimado(seg)']] \
                                                    .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                                                    .values

    Evaluacion_Hospitals_nearby_me['Ev_Distancia'] = Hospitals_nearby_me.reset_index() \
                                                    [['Distancia_Estimada(km)']] \
                                                    .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                                                    .values

    Evaluacion_Hospitals_nearby_me['Ev_Consultorios'] = Hospitals_nearby_me.reset_index() \
                                                    [['TOTAL_DE_CONSULTORIOS']] \
                                                    .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                                                    .values

    Evaluacion_Hospitals_nearby_me['Ev_Medicos'] = Hospitals_nearby_me.reset_index() \
                                                    [['TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS']] \
                                                    .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                                                    .values

    Evaluacion_Hospitals_nearby_me["Ev_Tiempo"] = (-1 * Evaluacion_Hospitals_nearby_me["Ev_Tiempo"])+1
    Evaluacion_Hospitals_nearby_me["Ev_Distancia"] = (-1 * Evaluacion_Hospitals_nearby_me["Ev_Distancia"])+1


    Evaluacion_Hospitals_nearby_me["Calificacion"] =(Evaluacion_Hospitals_nearby_me['Ev_Tiempo'] * 0.3
                                                    +Evaluacion_Hospitals_nearby_me['Ev_Distancia']* 0.1
                                                    +Evaluacion_Hospitals_nearby_me['Ev_Consultorios']* 0.1
                                                    +Evaluacion_Hospitals_nearby_me['Ev_Medicos']* 0.2)

    Evaluacion_Hospitals_nearby_me["Ranking"] = Evaluacion_Hospitals_nearby_me['Calificacion'].rank(method='max')
            
    print(Evaluacion_Hospitals_nearby_me.head(5))


    hcf = Evaluacion_Hospitals_nearby_me.to_json(orient='records')


    # # columns used for constructing geojson object
    # features = Evaluacion_Hospitals_nearby_me.apply(
    # lambda row: Feature(geometry=Point((float(row['LONGITUD']), float(row['LATITUD'])))),
    # axis=1).tolist()

    # # all the other columns used as properties
    # properties = Evaluacion_Hospitals_nearby_me.drop(['LATITUD', 'LONGITUD'], axis=1).to_dict('records')

    # # whole geojson object
    # hcf = FeatureCollection(features=features, properties=properties)

    # print(hcf)




    return render(request, 'rutas/resultado.html', {'latitude':latitude, 'longitude':longitude, 'hcf':hcf})
    #return render(request, 'rutas/resultado.html', {'latitude':latitude, 'longitude':longitude, 'hcf':json.dumps(hcf)})


    return  HttpResponse('Las coordenadas ingresadas fueron: {}'.format(coords))



