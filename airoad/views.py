"""
    Ce module contient le code qui gere le Streaming
    - affichage temps réel d'un flux video sur une vue
    - analyse temps réel de la video (detection d'objets)
    - affichage temps réel des données de statistique sur une vue.

    Plus d'info:
     - coroutine                : https://docs.python.org/3/library/asyncio-task.html
     - versioning               : https://semver.org/
     - django asynchrone        : https://docs.djangoproject.com/fr/4.1/topics/async/
     - generateur/iterateur     : https://python.doctor/page-iterateurs-iterator-generateur-generator-python
     - StreamingHttpResponse    : https://andrewbrookins.com/django/how-does-djangos-streaminghttpresponse-work-exactly/#:~:text=What%20is%20a%20StreamingHttpResponse%3F,client%20in%20a%20single%20piece.
"""

# Django packages
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

# import inference module
from . import inference

# Packages pour le Streaming
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2

# Packages pour l'éxécusion asynchrone
import threading
from asgiref.sync import sync_to_async
import asyncio

# Packages pour le traitement de données
from django.http import JsonResponse

# Packages Systeme
import os
import time
from datetime import datetime

# Le modele
from .models import AIRoadStatistics


# gzip est un utilitaire de compression de données sans perte
@gzip.gzip_page
def index(request):
    """
        Cette fonction permet de faire le rendu de la page traffic.html
    """

    context_data = {}
    return render(request, 'traffic.html', context=context_data)


class VideoCameraStreamDetection(object):
    """
        Cette classe permet de gérer le découpage d'un flux vidéo (mp4) en une suite d'image
        Cette classe permet aussi de gérer l'inférence (appel api azure pour la detection d'objet)
    """

    def __init__(self, idRoad, video_file=''):
        """
            Cette methode permet d'initialiser un objet de type VideoCameraStreamDetection

            params:
                - idRoad (str)      : l'id de la route
                - video_file (str)  : le path de la video mp4 

            return : object
                - type : VideoCameraStreamDetection
        """

        # initialisation de la propriete idroad
        self.idroad = idRoad

        # initialisation de l'objet flux video
        self.video = None

        # initialisation de la proriete frame_per_second
        # (nombre de frame (image) par seconde)
        self.frame_per_second = 0

        # initialisation de la proriete rate
        # (vitesse de lecture de la video)
        self.rate = 0

        # une image dans le flux video
        self.frame = None

        # indique si la lecture d'une frame reussi ou non
        self.grabbed = False

        # initialisation des données de detection
        # de la derniere frame analysée
        self.ai_stats_last_frame = inference.DEFAULT_RESPONSE

        # si le path donné en parametre est un fichier
        if os.path.isfile(video_file):
            # Ouverture d'un fichier vidéo
            self.video = cv2.VideoCapture(video_file)

        # si le path donné en parametre n'est pas un fichier
        else:
            # afficher un message d'erreur dans les logs
            print(f"[Error] isfile : {video_file}")

            # lancer la webcam comme source video
            self.video = cv2.VideoCapture(0)

        # calculer le frame per second (nombre d'images par seconde)
        # pour cette video
        self.compute_fps()

        # lecture de la prochaine image du fichier vidéo
        # self.grabbed : True s'il y a succes
        (self.grabbed, self.frame) = self.video.read()

        # Création d'un thread qui permet de découper le flux video
        # en une suite d'image. Pour éviter de geler l'application
        self.next_trame_thread = threading.Thread(target=self.update, args=())
        self.next_trame_thread.start()  # on lance le thread

        # Création d'un thread qui permet d'analyser
        # le contenu de self.frame. Pour eviter de geler l'application
        # ce thread execute une fonction 'asyncio.run'
        # la fonction 'asyncio.run' execute une coroutine 'self.infere'
        # la coroutine 'self.infere' est chargée de ... (cfr la doc de la fonction)
        self.trame_inference_thread = threading.Thread(
            target=asyncio.run, args=(self.infere(),))
        self.trame_inference_thread.start()  # on lance le thread

    def __del__(self):
        # on ferme le flux vidéo lors de la suppression de l'objet.
        self.video.release()

    def compute_fps(self):
        """
            Cette methode permet de calculer le nombre de frames par seconde.
            C'est le nombre d'image que la video contien dans une seconde.

            return : int
        """
        # Detecter la version de OpenCV (Crf le lien en haut: versioning)
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        # Avec une webcam get(CV_CAP_PROP_FPS) ne fonctionne pas.

        # si la version majeur de OpenCv est inferieur à 3
        # Lire la version dans la variable 'CV_CAP_PROP_FPS'
        if int(major_ver) < 3:
            self.frame_per_second = self.video.get(cv2.cv.CV_CAP_PROP_FPS)
            print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(
                self.frame_per_second))

        # si la version majeur de OpenCv est supérieur à 2
        # Lire la version dans la variable 'CAP_PROP_FPS'
        else:
            self.frame_per_second = self.video.get(cv2.CAP_PROP_FPS)
            print(
                "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(self.frame_per_second))

        # mettre à jour la vitesse de lecture de la video.
        # si on a 30 images par seconde, chaque image prend 1/30 secondes.
        self.rate = 1 / self.frame_per_second

    def get_frame(self):
        """
            Cette methode permet de transformer une frame de la video,
            en une image binaire.

            return : jpeg.tobytes
        """

        # Recuperation de la derniere frame lue
        image = self.frame

        # transformation de la frame en une image de type 'jpg'
        _, jpeg = cv2.imencode('.jpg', image)

        # transformation de l'image 'jpg' en donnees binaires
        image_stream = jpeg.tobytes()

        # on retourne les données binaires de l'image
        # utile pour l'inference et l'affichage web.
        return image_stream

    def update(self):
        """
            Cette methode permet de lire les frames de la video
            La lecture se fait tant qu'il y a une frame à lire.
        """

        # la boucle infinie ne fait pas planter l'app
        # parce que cette methode s'execute dans un autre thread
        # (self.next_trame_thread)
        while True:
            # Lecture de la prochaine frame
            # (Cfr initialisation self.grabbed & self.frame)
            (self.grabbed, self.frame) = self.video.read()

            # fréquence d'affichage d'une trame
            # Cfr compute_fps
            time.sleep(self.rate)

    # Transformer la fonction synchrone 'infere' en une fonction asychrone
    # afin qu'elle soit considéré comme une coroutine
    # Cfr Le lien en haut "django asynchrone"
    @sync_to_async(thread_sensitive=True)
    def infere(self):
        """
            Cette methode permet d'analyser la dernier frame lue,
            afin de detecter les objets

            Cette fonction sauvegarde aussi les statistiques 
            dans la base de donne

            Cette methode analyse la derniere frame lue, 
            car analyser toutes les frames est trop couter.

            par exemple, il y a 30 frames en une seconde,
            les objets dans le monde réel ne se deplacent
            pas vite au bout d'une seconde.

            ce qui signifie que, dans une seconde, les 30 frames
            sont identiques si on doit considerer les objets
            qui apparaissent dans ces frames là.

            Ce qui fait que si on analyse les 30 frames contenues
            dans une seconde de video, c'est un vrai gaspillage.

            imaginons ceci : 
            1 appel à l'api coute 1$
            pour 30 images ca nous fait 1$ x 30 = 30$ par seconde

            au bout de 60 seconde 60 x 30 = 1800$
            au bout d'une heure 60 x 1800 = 108000$

            mais si au lieu d'analyser 30 images identiques,
            on analyse une seule image chaque seconde

            pour 30 images ca nous fait 1$ x 1 = 1$ par seconde

            au bout de 60 seconde 60 x 1 = 60$
            au bout d'une heure 60 x 60 = 3600$

            Alors 108000$ VS 3600 par heure.

            C'est 3000% moins cher que la premiere approche.

            et meme au bout de 2 secondes, les objets ne subissent pas
            un deplacement considerable, on peut encore etre plus economique.

            mais ce n'est pas seulement en terme de budget mais aussi en terme
            de temps de calcul.

        """
        # la boucle infinie ne fait pas planter l'app
        # parce que cette methode s'execute dans un autre thread
        # (self.trame_inference_thread)
        while True:
            # inference -> analyse de la derniere frame lue
            # Cfr la description de la methode
            results = inference.analyze_octet_stream_image(
                octet_stream_img=self.get_frame())

            try:
                # Récuperation du sous dictionnaire 'statistics'
                statistics = results['statistics']
            except Exception as error:
                # s'il y a une erreur quelconque
                # juste afficher un message d'erreur.
                print(f"[Error] : {error}")
            else:
                # s'il n'y a pas d'erreur

                # on sauvergarde les statistiques dans la database
                # Cfr la doc du modele 'AIRoadStatistics'
                AIRoadStatistics(
                    name=self.idroad,
                    nb_objects=statistics['objects'],
                    nb_cars=statistics['car'],
                    nb_persons=statistics['person'],
                    nb_motorcycles=statistics['motorcycle'],
                    nb_bicycles=statistics['bicycle'],

                ).save()


def gen(camera):
    """
        Cette fonction permet d'obtenir une suite de frame
        affichable dans une page web

        params :
            - camera : VideoCameraStreamDetection

        Cfr : generateur/iterateur
    """

    # la boucle permet de parcourir la video
    # tanqu'il y a un frame à lire
    while True:

        #  Cfr la doc de la methode: VideoCameraStreamDetection.get_frame
        frame = camera.get_frame()

        # retourne une frame formaté
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def traffic_stream_road_1(request):
    """
        Cette
    """
    video_file = os.path.join(settings.STATIC_ROOT, "videoTrafic.mp4")

    video_camera = VideoCameraStreamDetection(idRoad=1, video_file=video_file)

    # Une classe de réponse HTTP en continu avec un itérateur comme contenu.
    # Cet itérateur ne doit être utilisé qu'une seule fois, lorsque la réponse est transmise au client.
    # Cependant, il peut être ajouté ou remplacé par un nouvel itérateur qui englobe le contenu original
    # (ou produit un contenu entièrement nouveau).
    # Cfr lien en haut : StreamingHttpResponse
    return StreamingHttpResponse(gen(video_camera),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def cal_time(request):
    """
        Cette fonction permet de récupérer la datetime
        Utilisé dans le template traffic

        return: JsonResponse
            un dictionnaire qui contient datetime

            {
                "days": int,
                "hours": int,
                "minutes: int,
                "seconds": int,
            }
    """
    # Récuperation du datetime actuel
    now = datetime.now()

    # récupération des attributs
    time_dict = {'days': now.day, 'hours': now.hour,
                 'minutes': now.minute, 'seconds': now.second}

    # Json datas
    return JsonResponse(time_dict)


def road_statistiques(request, idroad):
    """
        Cette fonction permet de récuperer,
        le dernier enregistrement des statistuques
        d'une route dans la base de donnee,

        params:
            - idrod : identifiant de la route

        return: JsonResponse

        Les donnees statistiques
        {
            # Nombre total d'objets detectés
            'objects': 0,

            # Nombre total des voitures detectées
            'car': 0,

            # Nombre total des personnes detectées
            'person': 0,

            # Nombre total des motos detectées
            'motorcycle': 0,

            # Nombre total des vélos detectés
            'bicycle': 0
        }

    """

    # on copie le schema de la reponse
    response = inference.DEFAULT_RESPONSE['statistics']

    # on gere les erreur pour eviter de geler l'app
    try:

        # recuperation de la derniere enregistrement
        # filtre : name, nb_intaje_date 
        # ce qui signifie, le dernier enregistrement en date
        # de la route 'name'
        latest_stats = AIRoadStatistics.objects.latest(
            'name', 'nb_intake_dates')

        # on formate la reponse
        response = {
            'objects': latest_stats.nb_objects,
            'car': latest_stats.nb_cars,
            'person': latest_stats.nb_persons,
            'motorcycle': latest_stats.nb_motorcycles,
            'bicycle': latest_stats.nb_bicycles
        }

    # en cas d'erreur
    except Exception as error:
        # renvoyer les donnees par defaut

        response = inference.DEFAULT_RESPONSE['statistics']

        # afficher un message dans les logs
        print(f"Retrieve Error : {error}")

    # retourner la reponse
    return JsonResponse(response)
