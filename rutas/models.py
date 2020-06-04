from django.db import models

# Create your models here.

class Hospital(models.Model):
    AÑO = models.IntegerField()
    CLUES = models.CharField(max_length=15)
    CLAVE_INSTUTUCION = models.CharField(max_length=10)
    CLAVE_MUNICIPIO = models.IntegerField()
    LATITUD = models.FloatField(max_length=15)
    LONGITUD = models.FloatField(max_length=15)
    DISTANCIA  = models.FloatField(max_length=5)
    TIEMPO_TRANSLADO = models.FloatField(max_length=5)
    NOMBRE_DE_LA_UNIDAD = models.CharField(max_length=150)
    TOTAL_DE_CONSULTORIOS = models.IntegerField()
    TOTAL_CAMAS_AREA_HOSPITALIZACION = models.IntegerField()
    TOTAL_CAMAS_EN_OTRAS_AREAS_NO_HOSP = models.IntegerField()
    TOTAL_MEDICOS_GENERALES_Y_ESPECIALISTAS = models.IntegerField()
    TOTAL_DE_ENFERMERAS_EN_CONTACTO_CON_EL_PACIENTE = models.IntegerField()