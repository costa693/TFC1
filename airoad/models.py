from django.db import models
from django.urls import reverse

# Create your models here.

class AIRoadStatistics(models.Model):
    # Le nom de la route
    name = models.CharField(max_length=200)

    # Le nombre total d'objet
    nb_objects = models.IntegerField(verbose_name="Number of objects")

    # Le nombre total des voitures
    nb_cars = models.IntegerField(verbose_name="Number of cars")

    # Le nombre total des personnes
    nb_persons = models.IntegerField(verbose_name="Number of persons")

    # Le nombre total des motos
    nb_motorcycles = models.IntegerField(verbose_name="Number of motorcycles")

    # Le nombre total des vélos
    nb_bicycles = models.IntegerField(verbose_name="Number of bicycles")

    # Date lors de la création de l'instance.
    nb_intake_dates = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    # def get_absolute_url(self):
    #     return reverse('airoad_detail', kwargs={"pk": self.pk})

