# Vistas de rutas
# Imports de Django
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files import File
from django.views.generic.base import TemplateView
# Vista como lista
from django.views.generic import ListView
# Formularios
from rutas.forms import CalculoForm
# Imports para el proyecto
from django.db import models
from rutas.models import Hospital
import os
import xlrd
import pandas as pd
from rutas.models import Calculo
#Importando librerias
import django_pandas as dpd
from django_pandas.io import read_frame
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import time
from sklearn.cluster import MiniBatchKMeans, KMeans
from sklearn.neighbors import NearestNeighbors
import timeit
from sklearn.model_selection import train_test_split
from sklearn import linear_model
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

    request.session.set_test_cookie()
    return render(request, 'rutas/rutas.html')

class RutaListView(ListView):
    model = Calculo
    form_class = CalculoForm
    template = 'rutas/rutas.html'

   
def resultado(request):
    longitude = float(request.POST.get('lnging'))
    latitude = float(request.POST.get('lating'))

    #Porcentajes de Preferencia, dados por el usuario. En esta etapa fueron definidos por el equipo
    pref_Tiempo = 0.4
    pref_Distancia = 0.15
    pref_Consultorio = 0.15
    pref_Medicos = 0.3

    # Importar datos  
    qs = Hospital.objects.all()
    df_Hospitals = read_frame(qs)
    # Se eliminó un print hospitals
    df_Hospitals = pd.DataFrame(df_Hospitals)
    df_Hospitals.head(5)

    # Juntando las coordenadas de los hospitales en un solo dataframe que es utilizado por el algoritmo de Nearest Neighbors
    df_LatitudHospitals = pd.DataFrame(df_Hospitals['LATITUD'])
    df_LongitudHospitals = pd.DataFrame(df_Hospitals['LONGITUD'])
    df_coordenadasHospitals = df_LatitudHospitals.join(df_LongitudHospitals)

    Ev_hospitales = df_Hospitals

    # Percentrank(Evaluacion) de los parametros Total de Consultorios y Medicos Generales (Variables Estaticas)

    Ev_hospitales['Ev_Consultorios'] = Ev_hospitales.reset_index() \
                                    [['TOTAL_DE_CONSULTORIOS']] \
                                    .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                                    .values

    Ev_hospitales['Ev_Medicos'] = Ev_hospitales.reset_index() \
                                [['TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS']] \
                                .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                                .values

    # Se añade Calificacion al dataframe de evaluación la cual suma de estos dos parametros multiplicado por
    #su factor de preferencia
    Ev_hospitales["Calificacion"] =( (Ev_hospitales['Ev_Consultorios']* pref_Consultorio)
                                                    +(Ev_hospitales['Ev_Medicos']* pref_Medicos))
    
    #Solamente se seleccionaran los 10 neighbors mas cercanos
    nbrs = NearestNeighbors(n_neighbors=15, algorithm='auto').fit(df_coordenadasHospitals)

    X = Ev_hospitales[['TOTAL_DE_CONSULTORIOS','TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS']]
    y = Ev_hospitales['Calificacion']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=417)

    regr = linear_model.BayesianRidge()
    reg = regr.fit(X_train, y_train)
    y_pred = reg.predict(X_test)

  
    def funcionEvaluacion(df_my_location):
    #Entrenamiento no supervisado del algoritmo K Nearest Neighbor
        distances, indices = nbrs.kneighbors(df_my_location)
        df_Out = pd.DataFrame(indices)
        df_Out = df_Out.T
        df_Out = df_Out.rename({0: "Indice"}, axis='columns')
        # Se empieza crear el dataframe final el cual va a contener toda la informacion de salida
        # La API añade los tiempos de traslado y distancia al dataframe
        
        for i in df_Out.index:
            indice = df_Out.iat[i,0]
            df_Out.at[i, 'LATITUD'] = df_Hospitals.iat[indice,5]  
            df_Out.at[i, 'LONGITUD'] = df_Hospitals.iat[indice,6]  
            df_Out.at[i, 'NOMBRE_DE_LA_UNIDAD'] = df_Hospitals.iat[indice,9]   
            df_Out.at[i, 'TOTAL_DE_CONSULTORIOS'] = df_Hospitals.iat[indice,10]
            df_Out.at[i, 'TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS'] = df_Hospitals.iat[indice,13]   
            hospital_location = (df_Hospitals.iat[indice,5], df_Hospitals.iat[indice,6])
            df_Out.at[i, 'Tiempo_Estimado(seg)'] = bing.travelTime(my_location, hospital_location )
            df_Out.at[i, 'Distancia_Estimada(km)'] = bing.travelDistance(my_location, hospital_location)
        #Se hace la prediccion de las calificaciones mediante el algoritmo de Bayesian Ridge Regressor       
        pred = df_Out[['TOTAL_DE_CONSULTORIOS','TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS']]
        df_Out["Calificacion"] = reg.predict(pred)
        
        # Haciendo el PercentRank de las variables que no son estaticas sobre el data frame ya filtrado de los nearest neighbors
        df_Out['Ev_Tiempo'] = df_Out.reset_index() \
                            [['Tiempo_Estimado(seg)']] \
                            .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                            .values

        df_Out['Ev_Distancia'] = df_Out.reset_index() \
                                [['Distancia_Estimada(km)']] \
                                .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
                                .values
        
        # Aquellos parametros que sean los menores seran los que tengan la maxima calificacion
        df_Out["Ev_Tiempo"] = (-1 * df_Out["Ev_Tiempo"])+1
        df_Out["Ev_Distancia"] = (-1 * df_Out["Ev_Distancia"])+1
        
        # Sumando todas las calificaciones y multiplicandolas por su factor de preferencia para obtener la calificacion final
        for i in df_Out.index:
            df_Out["Calificacion_Final"] =( df_Out['Ev_Tiempo'] * pref_Tiempo
                                        +df_Out['Ev_Distancia']* pref_Distancia
                                        +df_Out['Calificacion'])
            
        df_Out = df_Out.drop(['Calificacion'], axis=1)
        df_Out = df_Out.drop(['Ev_Tiempo'], axis=1)
        df_Out = df_Out.drop(['Ev_Distancia'], axis=1)

            
        #Haciendo el rankeo final con las calificaciones finales obtenidas
        df_Out["Ranking"] = df_Out['Calificacion_Final'].rank(method='dense', ascending = False)

        result = df_Out
        return result

    #Inicializacion de variables de tu posicion
    my_latitude = latitude
    my_longitude = longitude
    my_location = (my_latitude, my_longitude)
    df_my_location = pd.DataFrame({'Latitud': [my_latitude],'Longitud': [my_longitude]})
    df_Output = funcionEvaluacion(df_my_location)

    hcf = df_Output.sort_values(["Ranking"], ascending=True)
    hcf = hcf.head(3)
    print(hcf)
    hcf = hcf.to_json(orient='records')  

   
    # Muestra de la vista pasando los parámetros de localización y el resultado del modelo
    return render(request, 'rutas/resultado.html', {'latitude':latitude, 'longitude':longitude, 'hcf':hcf})
   
    return  HttpResponse('Las coordenadas ingresadas fueron: {}'.format(coords))

    


# def resultado(request):

    # longitude = float(request.POST.get('lnging'))
    # latitude = float(request.POST.get('lating'))

    # coords = {"latitude":latitude,"longitude":longitude}
    # print(coords)
    
    # #Inicializacion de variables de tu posicion
    # my_latitude = latitude
    # my_longitude = longitude
    # my_location = (my_latitude, my_longitude)
    # np_my_location_arr = np.array([my_latitude,my_longitude])
    # df_my_location = pd.DataFrame({'Latitud': [my_latitude],'Longitud': [my_longitude]})
   
    # #Importando los datos y convirtiendolo en un dataframe
     
    # qs = Hospital.objects.all()
    # df_Hospitals = read_frame(qs)
    # # Se eliminó un print hospitals
    # df_Hospitals = pd.DataFrame(df_Hospitals)

    # #Juntando los datos de las localizaciones del hospital que nutren al algoritmo de Kmeans
    # df_LatitudHospitals = pd.DataFrame(df_Hospitals['LATITUD'])
    # df_LongitudHospitals = pd.DataFrame(df_Hospitals['LONGITUD'])
    # df_coordenadasHospitals = df_LatitudHospitals.join(df_LongitudHospitals)
    # # Elminación de print del df
    # #Se ejecutara 2 veces, la primera vez el algoritmo para conseguir los centros y la segunda vez para incluir la posicion
    # #en la que nos encontramos como un centro
    # k_means1 = KMeans(init='k-means++', n_clusters=10, n_init=10)
    # k_means1.fit(df_coordenadasHospitals)
    # y_kmeans1 = k_means1.predict(df_coordenadasHospitals)
    # centers = k_means1.cluster_centers_
    # print(centers)
    # newcenters = np.insert(centers, 0, np_my_location_arr, axis=0)
    # print(newcenters)
    # # Definición de nuevos centroides
    # newcenters = np.insert(centers, 0, np_my_location_arr, axis=0)
    # newcenters
    # # 
    # k_means2 = KMeans(init=newcenters, n_clusters=11, n_init=1)
    # k_means2.fit(df_coordenadasHospitals)
    # y_kmeans2 = k_means2.predict(df_coordenadasHospitals)
    # # Resultados de Kmeans
    # df_Outputs_KMeans = pd.DataFrame(df_Hospitals['NOMBRE_DE_LA_UNIDAD'])
    # df_Outputs_KMeans = df_Outputs_KMeans.join(pd.DataFrame(df_Hospitals['LATITUD']))
    # df_Outputs_KMeans = df_Outputs_KMeans.join(pd.DataFrame(df_Hospitals['LONGITUD']))
    # df_Outputs_KMeans = df_Outputs_KMeans.join(pd.DataFrame(data=y_kmeans2, columns=["Center_Index"]))
   
    # # Predicción 
    # closest_cluster_center = k_means2.predict(df_my_location)
    # # 
    # LocateCenters = df_Outputs_KMeans.loc[df_Outputs_KMeans["Center_Index"] == closest_cluster_center[0]] 
    # LocateCenters = LocateCenters.reset_index()
    # LocateCenters = LocateCenters.drop(['index'], axis=1)
    # LocateCenters = LocateCenters.drop(['Center_Index'], axis=1)
    # # 
    # for i in LocateCenters.index:
    #     hospital_location = (LocateCenters.iat[i,1], LocateCenters.iat[i,2])
    #     LocateCenters.at[i, 'Tiempo_Estimado(seg)'] = bing.travelTime(my_location, hospital_location )
    #     LocateCenters.at[i, 'Distancia_Estimada(km)'] = bing.travelDistance(my_location, hospital_location)
    # # Evaluación de parámetros
    # Hospitals_nearby_me = LocateCenters
    # # Hospitals_nearby_me = LocateCenters.drop(['LATITUD'], axis=1)
    # # Hospitals_nearby_me = Hospitals_nearby_me.drop(['LONGITUD'], axis=1)
    # Hospitals_nearby_me = Hospitals_nearby_me.join(pd.DataFrame(df_Hospitals['TOTAL_DE_CONSULTORIOS']))
    # Hospitals_nearby_me = Hospitals_nearby_me.join(pd.DataFrame(df_Hospitals['TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS']))
    # Hospitals_nearby_me
    # #Preferencias Funcion de Evaluacion
    # #30% Tiempo de Traslado
    # #10% Distancia de Traslado
    # #10% Cantidad de Consultorios
    # #20% Cantidad de Medicos
    # #30% Ocupacion

    # Evaluacion_Hospitals_nearby_me = Hospitals_nearby_me
    # Evaluacion_Hospitals_nearby_me['Ev_Tiempo'] = Hospitals_nearby_me.reset_index() \
    #                                                 [['Tiempo_Estimado(seg)']] \
    #                                                 .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
    #                                                 .values

    # Evaluacion_Hospitals_nearby_me['Ev_Distancia'] = Hospitals_nearby_me.reset_index() \
    #                                                 [['Distancia_Estimada(km)']] \
    #                                                 .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
    #                                                 .values

    # Evaluacion_Hospitals_nearby_me['Ev_Consultorios'] = Hospitals_nearby_me.reset_index() \
    #                                                 [['TOTAL_DE_CONSULTORIOS']] \
    #                                                 .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
    #                                                 .values

    # Evaluacion_Hospitals_nearby_me['Ev_Medicos'] = Hospitals_nearby_me.reset_index() \
    #                                                 [['TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS']] \
    #                                                 .apply(lambda x: (x.rank(method='dense') - 1) / (x.nunique() - 1) ) \
    #                                                 .values

    # Evaluacion_Hospitals_nearby_me["Ev_Tiempo"] = (-1 * Evaluacion_Hospitals_nearby_me["Ev_Tiempo"])+1
    # Evaluacion_Hospitals_nearby_me["Ev_Distancia"] = (-1 * Evaluacion_Hospitals_nearby_me["Ev_Distancia"])+1


    # Evaluacion_Hospitals_nearby_me["Calificacion"] =(Evaluacion_Hospitals_nearby_me['Ev_Tiempo'] * 0.3
    #                                                 +Evaluacion_Hospitals_nearby_me['Ev_Distancia']* 0.1
    #                                                 +Evaluacion_Hospitals_nearby_me['Ev_Consultorios']* 0.1
    #                                                 +Evaluacion_Hospitals_nearby_me['Ev_Medicos']* 0.2)

    # Evaluacion_Hospitals_nearby_me["Ranking"] = Evaluacion_Hospitals_nearby_me['Calificacion'].rank(method='dense', ascending = False)

    # Evaluacion_Hospitals_nearby_me = Evaluacion_Hospitals_nearby_me.sort_values(["Ranking"], ascending=True)


            
    # print(Evaluacion_Hospitals_nearby_me.head(3))

    # hcf = Evaluacion_Hospitals_nearby_me.to_json(orient='records')


# Posible salida para formato GeoJson
    # # columns used for constructing geojson object
    # features = Evaluacion_Hospitals_nearby_me.apply(
    # lambda row: Feature(geometry=Point((float(row['LONGITUD']), float(row['LATITUD'])))),
    # axis=1).tolist()

    # # all the other columns used as properties
    # properties = Evaluacion_Hospitals_nearby_me.drop(['LATITUD', 'LONGITUD'], axis=1).to_dict('records')

    # # whole geojson object
    # hcf = FeatureCollection(features=features, properties=properties)

    # print(hcf)



    # # Muestra de la vista pasando los parámetros de localización y el resultado del modelo
    # return render(request, 'rutas/resultado.html', {'latitude':latitude, 'longitude':longitude, 'hcf':hcf})
   
    # return  HttpResponse('Las coordenadas ingresadas fueron: {}'.format(coords))



