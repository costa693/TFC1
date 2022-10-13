from django.shortcuts import render
import folium



# Create your views here.

def index(request):
    #create a map object
    m=folium.Map()
    m = m._repr_html_()
    context = {
        'm': m,

    }
    return render(request,'index.html',context)
