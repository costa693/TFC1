import inference

import json

IS_URL_IMG = True

if __name__ == '__main__':
    if IS_URL_IMG:
        # analyse url image
        response = inference.analize_url_image()
        # print response
        print(json.dumps(response, indent=4))

    else:
        response = inference.analyze_octet_stream_image()
        print(json.dumps(response, indent=4))
    