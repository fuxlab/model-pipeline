from flask import request
from flask_restful import Resource

from parse.parser import Parser
import requests
from PIL import Image

from flask import current_app as app

class PipelineView(Resource):
    

    def parse_image(self, image_data):
        '''
        parse image processing
        '''
        ret = {}
        image = False
        if 'url' in image_data:
            try:
                # imitate browser behaviour for cdn
                headers = {
                    #"content-type": "application/json"
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                }
                response = requests.get(image_data['url'], headers=headers, allow_redirects=True, stream = True)
                image = Image.open(response.raw)

                ret['width'] = image.width
                ret['height'] = image.height
            except:
                return False, False
        return ret, image


    def process(self, image, data={}):
        '''
        start processing pipeline
        '''
        parser = Parser(app.config['config'],
            image=image,
            model_endpoint=app.config['model_endpoint'],
            version=app.config['version'],
            data=data
        )
        result = parser.process()

        return result


    def post(self):
        '''
        parse request
        '''
        request_data = request.get_json(force=True)

        result = {}
        result['request'] = request_data

        if 'image' in request_data:
            (result['image'], image) = self.parse_image(request_data['image'])

            if result['image']:
                result = self.process(image, data=result)

        return result

