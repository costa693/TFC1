from django.db import models
from django.urls import reverse

# Create your models here.

class AIRoadStatistics(models.Model):
    name = models.CharField(max_length=200)
    nb_objects = models.IntegerField(verbose_name="Number of objects")
    nb_cars = models.IntegerField(verbose_name="Number of cars")
    nb_persons = models.IntegerField(verbose_name="Number of persons")
    nb_motorcycles = models.IntegerField(verbose_name="Number of motorcycles")
    nb_bicycles = models.IntegerField(verbose_name="Number of bicycles")
    nb_intake_dates = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    # def get_absolute_url(self):
    #     return reverse('airoad_detail', kwargs={"pk": self.pk})

