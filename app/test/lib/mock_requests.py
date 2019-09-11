import json
import httpretty

from api import app

from parse.config import Config
from parse.parser import Parser


def mock_model_response(model_response):
    '''
    
    '''
    for model, response_data in model_response.items():
        httpretty.register_uri(
            httpretty.POST,
            Parser([], model_endpoint=app.config['model_endpoint'], version=app.config['version']).model_url(model),
            status=200,
            body=json.dumps(response_data)
        )


def mock_error_response(request_url):
    '''
    fake error response
    '''
    httpretty.register_uri(
        httpretty.GET,
        request_url,
        status=404
    )


def mock_image_response(request_url, response_file, image_type='jpeg'):
    '''
    fake image responce from remote server with image file
    '''
    with open(response_file, 'rb') as img1:
        img_content = img1.read()
    
    httpretty.register_uri(
        httpretty.GET,
        request_url,
        status=200,
        body=img_content,
        content_type='image/%s' % (image_type)
    )
