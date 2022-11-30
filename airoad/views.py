from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

# import inference module
from . import inference

# for stream
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2

# async
import threading
from asgiref.sync import sync_to_async
import asyncio

from django.http import JsonResponse
from datetime import datetime

# model
from .models import AIRoadStatistics

video_camera_objects = {
    "camera_road_1": None,
    "camera_road_2": None,
    "camera_road_3": None,
    "camera_road_4": None,
}


@gzip.gzip_page
def index(request):
    context_data = {
        "idroads": [1, 2],
    }
    return render(request, 'traffic.html', context=context_data)


class VideoCamera(object):
    def __init__(self, idRoad, video_file=None):

        # id road
        self.idroad = idRoad

        # ai response
        self.ai_stats = inference.DEFAULT_RESPONSE

        if video_file == None:
            self.video = cv2.VideoCapture(0)
        else:
            self.video = cv2.VideoCapture(video_file)

        (self.grabbed, self.frame) = self.video.read()

        # get next frame thread
        threading.Thread(target=self.update, args=()).start()
        # threading.Thread(target=self.infere, args=()).start()

        # inference thread
        # threading.Thread(target=self.infere, args=(self,)).start()
        threading.Thread(target=asyncio.run, args=(self.infere(),)).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)

        image_stream = jpeg.tobytes()

        return image_stream

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

            # analyse image
            # asyncio.run(self.infere())
    
    def save_data(self):
        while True:
            asyncio.run(self.infere())
            
    @sync_to_async(thread_sensitive=True)
    def infere(self):
        # response = inference.analyze_octet_stream_image

        while True:
            # results = await sync_to_async(inference.analyze_octet_stream_image, thread_sensitive=True)(octet_stream_img=self.frame)
            results = inference.analyze_octet_stream_image(octet_stream_img=self.get_frame())

            try:
                # save results
                statistics = results['statistics']
            except Exception as error:
                print(f"[Error] : {error}")
            else:
                AIRoadStatistics(
                    name=self.idroad,
                    nb_objects=statistics['objects'],
                    nb_cars=statistics['car'],
                    nb_persons=statistics['person'],
                    nb_motorcycles=statistics['motorcycle'],
                    nb_bicycles=statistics['bicycle'],

                ).save()


def gen(camera):
    while True:
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def traffic_stream_road_1(request):
    # global video_camera_objects

    video_camera = VideoCamera(idRoad=1)

    # video_camera_objects['camera_road_1'] = video_camera

    return StreamingHttpResponse(gen(video_camera),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def cal_time(request):
    # Time Calculations Performed Here
    now = datetime.now()
    time_dict = {'days': now.day, 'hours': now.hour,
                 'minutes': now.minute, 'seconds': now.second}
    return JsonResponse(time_dict)


def road_statistiques(request, idroad):

    response = inference.DEFAULT_RESPONSE['statistics']

    return JsonResponse(response)
