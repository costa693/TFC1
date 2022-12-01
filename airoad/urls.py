from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('traffic_stream_road_1', views.traffic_stream_road_1, name='traffic_stream_road_1'),
    path('road_statistiques/<int:idroad>', views.road_statistiques, name='road_statistiques'),
    path('cal_time', views.cal_time, name='cal_time'),
    # cal_time
]