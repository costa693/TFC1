from multiprocessing import context
from telnetlib import SE
from django.shortcuts import render
import folium
import geocoder
from geolocate.models import Search

# Create your views here.

def index(request):
    adress = Search.objects.all().last
    location = geocoder.osm('zambia')
    lat = location.lat
    lng = location.lng
    country = location.country
    town =location.town
    #create a map object
    m=folium.Map(location=[19, -12], zoom_start = 2)
    #folium.Marker([-11.664722, 27.479444 ], tooltip='click for more',
    #popup='Lubumbashi').add_to(m)

    folium.Marker([lat,lng], tooltip='click for more',popup=country).add_to(m)
    folium.Marker([lat,lng], tooltip='click for more',popup=town).add_to(m)

        #Get html Representation of map Object
    m = m._repr_html_()
    context={
        'm': m,
    }
    return render(request,'index.html', context)
