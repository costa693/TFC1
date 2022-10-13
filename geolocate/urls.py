from importlib.resources import path
from django.urls import path
from django.contrib import admin
#from .views import index
from .import views

urlpatterns=[
     path('admin/',admin.site.urls),
     


]