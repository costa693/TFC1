from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import json
import requests
import copy
'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = "1c481c40dcef4d03a49d7858b54f1d89"
endpoint = "https://consta-tfe-cv.cognitiveservices.azure.com/"

# analyze url
ANALYZE_URL = f'{endpoint}vision/v3.2/analyze'

computervision_client = ComputerVisionClient(
    endpoint, CognitiveServicesCredentials(subscription_key))
'''
END - Authenticate
'''

'''
OCR: Read File using the Read API, extract text - remote
This example will extract text in an image, then print results, line by line.
This API call can also extract handwriting style text (not shown).
'''
print("===== Analyse File - remote =====")
# Get an image with text
DEFAULT_IMG_URL = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"
DEFAULT_IMG_URL = "https://media.gettyimages.com/photos/cars-in-rush-hour-with-traffic-at-dawn-picture-id155287967?s=612x612"
DEFAULT_IMG_URL = "https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/images/windows-kitchen.jpg"
DEFAULT_IMG_URL = "https://lh4.googleusercontent.com/-UMwfTuruVrM/Tf8hhdLf-8I/AAAAAAAAKSA/IddvXSjfBug/IMG_4120.JPG"
DEFAULT_IMG_URL = "https://www.francetvinfo.fr/pictures/EP91ws0bTR1ZJ5z71TAgQ4QZV7M/1200x1200/2022/09/20/phpEIBJEM.jpg"
# DEFAULT_IMG_URL = "https://cdn.who.int/media/images/default-source/imported/pedestrians-road-traffic-jpg.jpg?sfvrsn=132b8496_2"

DEFAULT_RESPONSE = {
    'objects': {
        'car': [
            # {
            #     'x': detected_object.rectangle.x,
            #     'y': detected_object.rectangle.y,
            #     'w': detected_object.rectangle.w,
            #     'h': detected_object.rectangle.h,
            #     'confidence': detected_object.confidence,
            # }
        ],
        'person': [],
        'motorcycle': [],
        'bicycle': [],
    },
    'statistics':
        {
            'objects': 0,
            'car': 0,
            'person': 0,
            'motorcycle': 0,
            'bicycle': 0
    }
}


def compute_statistics(data):
    response = copy.deepcopy(data)
    # statistics
    for key in response['statistics'].keys():
        if key == 'objects':
            pass
        else:
            response['statistics'][key] += len(response['objects'][key])
            response['statistics']['objects'] += response['statistics'][key]

    return response


def analyze_octet_stream_image(octet_stream_img=None):

    if octet_stream_img == None:
        # application/octet-stream
        read_image_url = '/home/nathanbangwa/Pictures/me.jpeg'

        octet_stream_img = open(read_image_url, "rb").read()

    # copy default response deeply
    response = copy.deepcopy(DEFAULT_RESPONSE)

    # http headers
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream'
    }

    # http parameters
    params = {
        'visualFeatures': 'Objects'
    }

    try:
        # http request for inference
        http_response = requests.post(
            ANALYZE_URL, headers=headers, params=params, data=octet_stream_img)
    except requests.exceptions.SSLError as error:
        print(f"Network Error : {error}")
        return DEFAULT_RESPONSE

    http_response.raise_for_status()

    # The 'analysis' detected_object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    http_response_json = http_response.json()

    for detected_object in http_response_json['objects']:
        object_tag = detected_object['object']
        if object_tag in response['objects'].keys():
            response['objects'][object_tag].append(
                {
                    'x': detected_object['rectangle']['x'],
                    'y': detected_object['rectangle']['y'],
                    'w': detected_object['rectangle']['w'],
                    'h': detected_object['rectangle']['h'],
                    'confidence': detected_object['confidence'],
                }
            )
        else:
            print(f"Not found : {detected_object['object']}")

    response = compute_statistics(response)

    return response


def analize_url_image(read_image_url=DEFAULT_IMG_URL):
    image_analysis = computervision_client.analyze_image(
        read_image_url, visual_features=[VisualFeatureTypes.objects])

    # copy default response deeply
    response = copy.deepcopy(DEFAULT_RESPONSE)

    for detected_object in image_analysis.objects:
        if detected_object.object_property in response['objects'].keys():
            response['objects'][detected_object.object_property].append(
                {
                    'x': detected_object.rectangle.x,
                    'y': detected_object.rectangle.y,
                    'w': detected_object.rectangle.w,
                    'h': detected_object.rectangle.h,
                    'confidence': detected_object.confidence,
                }
            )
        else:
            print(f"Not found : {detected_object.object_property}")

    response = compute_statistics(response)

    # response
    return response


'''
END - Analyse File - remote
'''

print("End of Computer Vision quickstart.")
