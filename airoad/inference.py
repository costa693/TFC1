"""
    Ce module permet de detecter des objets contenus dans une image.
    Ce module utilise le service cognitive d'Azure.

    Ce module contient 2 fonctions principales:
    - analyze_octet_stream_image : permet d'analyser une image type bytes
    - analize_url_image : permet d'annalyser une image type url.

    Les objets detectés sont:
    - car : les voitures en général
    - person : les personnes
    - motorcycle : Les motos
    - bicycle : Les vélos 

    Plus d'infos ici : 
    https://learn.microsoft.com/fr-fr/azure/cognitive-services/computer-vision/concept-object-detection?tabs=4-0

    https://learn.microsoft.com/fr-fr/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision?view=azure-python
"""


# Azure Packages | Cfr les liens ci-haut.
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

# Packages pour le traitement des données.
import json
import requests
import copy


'''
Authentification

Authentifie vos informations d'identification et crée un client.
'''

# La clé azure pour se communiquer avec le service azure (ceci est une clé temporaire)
subscription_key = "1c481c40dcef4d03a49d7858b54f1d89"

# Le point d'entrer du service azure
endpoint = "https://consta-tfe-cv.cognitiveservices.azure.com/"

# Adresse URL de l'api de detection d'objet
ANALYZE_URL = f'{endpoint}vision/v3.2/analyze'

# Création du client azure computer vision.
computervision_client = ComputerVisionClient(
    endpoint, CognitiveServicesCredentials(subscription_key))

# Les images pour le test de la fonction -> analize_url_image
DEFAULT_IMG_URL = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"
DEFAULT_IMG_URL = "https://media.gettyimages.com/photos/cars-in-rush-hour-with-traffic-at-dawn-picture-id155287967?s=612x612"
DEFAULT_IMG_URL = "https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/images/windows-kitchen.jpg"
DEFAULT_IMG_URL = "https://lh4.googleusercontent.com/-UMwfTuruVrM/Tf8hhdLf-8I/AAAAAAAAKSA/IddvXSjfBug/IMG_4120.JPG"
DEFAULT_IMG_URL = "https://www.francetvinfo.fr/pictures/EP91ws0bTR1ZJ5z71TAgQ4QZV7M/1200x1200/2022/09/20/phpEIBJEM.jpg"
DEFAULT_IMG_URL = "https://cdn.who.int/media/images/default-source/imported/pedestrians-road-traffic-jpg.jpg?sfvrsn=132b8496_2"


# Le schema des données qui seront retournées par les 2 fonctions d'analyse

DEFAULT_RESPONSE = {

    # Les objets detecté

    'objects': {

        # La liste des voitures
        'car': [
            # {
            #     'x': int,             -> La position verticale de l'objet
            #     'y': int,             -> La position horizontale de l'objet
            #     'w': int,             -> La largeur de l'objet
            #     'h': int,             -> la hauteur de l'objet
            #     'confidence': float,  -> La précision de la detection en pourcentage
            # }
        ],

        # La liste des personnes
        'person': [],

        # La liste des motos
        'motorcycle': [],

        # La liste des vélos
        'bicycle': [],
    },

    # Les données statistiques
    'statistics':
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
}

# Les objets considérés comme des voitures
# Pour éviter de gérer individuellement plusieurs objets d'une meme nature
vehicule_objects = [
    'Van',
    'Land vehicle',
    'taxi',
]


def compute_statistics(data: dict) -> dict:
    """
        Cette fonction permet de compiler les statistiques.

        return: dict
        - ce dictionnaire est semblable a DEFAULT_RESPONSE
    """

    # On fait la copie profonde des données pour éviter de modifier le dictionnaire de depart.
    # en d'autre termes, on copie les données sans copier les références des données dans la memoire Ram.
    response = copy.deepcopy(data)

    # On calcule les statistiques

    # on parcours toutes les clés du sous dictionnaire statistique
    for key in response['statistics'].keys():

        # si la clé c'est objects on ne fait rien
        # car c'est la somme des autres clés.
        if key == 'objects':
            pass

        # si la clé est [car, person, motorcycle, bicycle]
        else:
            # On calcule la somme d'objet qui ont étaient detectés dans cette categorie
            response['statistics'][key] += len(response['objects'][key])

            # on met à jour le nombre total d'objets en ajoutant les objets de cette dite categorie.
            response['statistics']['objects'] += response['statistics'][key]

    # on retourne le dictionnaire de type DEFAULT_RESPONSE
    return response


def analyze_octet_stream_image(octet_stream_img: bytes = None) -> dict:
    """
        Cette fonction permet d'analyser une image de type bytes.

        Params
         - octet_stream_img : image de type byte

        return: dict
        - ce dictionnaire est semblable a DEFAULT_RESPONSE
    """

    # S'il n'y a aucune image à analyser
    if octet_stream_img == None:

        # on retourne le dictionnaire par defaut.
        return DEFAULT_RESPONSE

    # On fait la copie profonde des données pour éviter de modifier le dictionnaire de depart.
    # en d'autre termes, on copie les données sans copier les références des données dans la memoire Ram.
    response = copy.deepcopy(DEFAULT_RESPONSE)

    # Les en-tete HTTP (ou http headers)
    headers = {
        # La clé d'authentification Azure
        'Ocp-Apim-Subscription-Key': subscription_key,

        # Le type de contenu (dans ce cas, c'est une image binaire)
        'Content-Type': 'application/octet-stream'
    }

    # Les parametres http (ou http parameters)
    params = {
        # Les types de caracteristique visuel que l'on veut detecter
        # Dans ce cas, nous voulons detecter des objets

        'visualFeatures': 'Objects'
    }

    # On fait une gestion d'erreur pour eviter que l'application plante
    try:
        # Inférence : on envoie la requete http POST au service azure de detection d'objet.
        http_response = requests.post(
            ANALYZE_URL, headers=headers, params=params, data=octet_stream_img)
    
    except requests.exceptions.SSLError as error:
        # S'il y a une erreur reseau (par exemple la machine n'est pas connectée)
        # (utile losque on fait des tests en localhost et qu'on a pas besoin de faire de detection en ligne)

        # on affiche ça dans les infos de logs
        print(f"Network Error : {error}")

        # on retourne les donnees par defaut.
        return DEFAULT_RESPONSE

    # Lève l'erreur HTTPError, s'il y en a une.
    http_response.raise_for_status()

    # On recupere les données d'analyse envoyées par le service Azure.
    http_response_json = http_response.json()

    
    # On construit le dictionnaire reponse

    # on iter sur les éléments du sous dictionnaire 'objects'
    for detected_object in http_response_json['objects']:

        # On recupere le tag (la categorie de l'objet detecté)
        object_tag = detected_object['object']

        # si le tag de l'objet se trouve dans la liste ['Van', 'Land vehicle','taxi'] 
        # alors c'est une voiture, on change le tag, sinon on garde le tag
        object_tag = 'car' if object_tag in vehicule_objects else object_tag

        # si le tag se trouve dans le dictionnaire reponse par defaut
        if object_tag in response['objects'].keys():

            # On ajoute cet objet a la liste des objets similaires
            response['objects'][object_tag].append(
                {
                    'x': detected_object['rectangle']['x'],         # -> La position verticale de l'objet 
                    'y': detected_object['rectangle']['y'],         # -> La position horizontale de l'objet
                    'w': detected_object['rectangle']['w'],         # -> La largeur de l'objet
                    'h': detected_object['rectangle']['h'],         # -> la hauteur de l'objet
                    'confidence': detected_object['confidence'],    # -> La précision de la detection en pourcentage
                }
            )

        # si le tag ne se trouve dans le dictionnaire reponse par defaut
        else:
            # afficher un message dans le log pour notifier que le tag n'est pas parmi les objets à detecter.
            # exemple, les oiseaux n'entre pas dans les criteres pour changer l'état d'un feu de signalisation
            print(f"Not found : {detected_object['object']}")
    
    # On calcule (ajoute) les statistiques
    response = compute_statistics(response)

    # on retourne le dictionnaire de type DEFAULT_RESPONSE
    return response


def analize_url_image(read_image_url=DEFAULT_IMG_URL):
    """
        Cette fonction permet d'analyser une image de type url.

        Params
         - read_image_url : url d'une image en ligne

        return: dict
        - ce dictionnaire est semblable a DEFAULT_RESPONSE
    """

    # Inférence : on envoie la requete au service azure de detection d'objet.
    # visual_features -> Les types de caracteristique visuel que l'on veut detecter
    #                    Dans ce cas, nous voulons detecter des objets
    image_analysis = computervision_client.analyze_image(
        read_image_url, visual_features=[VisualFeatureTypes.objects])

    # On fait la copie profonde des données pour éviter de modifier le dictionnaire de depart.
    # en d'autre termes, on copie les données sans copier les références des données dans la memoire Ram.
    response = copy.deepcopy(DEFAULT_RESPONSE)

    # On construit le dictionnaire reponse
    # on iter sur les éléments de la propriete 'objects'
    for detected_object in image_analysis.objects:

        # On recupere le tag (la categorie de l'objet detecté)
        object_tag = detected_object.object_property

        # si le tag de l'objet se trouve dans la liste ['Van', 'Land vehicle','taxi'] 
        # alors c'est une voiture, on change le tag, sinon on garde le tag
        object_tag = 'car' if object_tag in vehicule_objects else object_tag

        # si le tag se trouve dans le dictionnaire reponse par defaut
        if object_tag in response['objects'].keys():
            response['objects'][detected_object.object_property].append(
                {
                    'x': detected_object.rectangle.x,           # -> La position verticale de l'objet  
                    'y': detected_object.rectangle.y,           # -> La position horizontale de l'objet
                    'w': detected_object.rectangle.w,           # -> La largeur de l'objet 
                    'h': detected_object.rectangle.h,           # -> la hauteur de l'objet
                    'confidence': detected_object.confidence,   # -> La précision de la detection en pourcentage
                }
            )

        # si le tag ne se trouve dans le dictionnaire reponse par defaut
        else:
            # afficher un message dans le log pour notifier que le tag n'est pas parmi les objets à detecter.
            # exemple, les oiseaux n'entre pas dans les criteres pour changer l'état d'un feu de signalisation
            print(f"Not found : {detected_object.object_property}")

    # On calcule (ajoute) les statistiques
    response = compute_statistics(response)

    # on retourne le dictionnaire de type DEFAULT_RESPONSE
    return response
