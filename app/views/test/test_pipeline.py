import warnings, json
import unittest
import httpretty

from api import app
from test.lib.mock_requests import mock_image_response, mock_error_response
from parse.config import Config


class TestPipeline(unittest.TestCase):


    def setUp(self):
        app.config['config'] = Config({})

        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed*")
        self.app = app
        self.client = self.app.test_client()

    
    def test_default_response(self):
        data = {
            'key': 'value'
        }
        resp = self.client.post(path='/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        response_data = json.loads(resp.get_data(as_text=True))
        self.assertEqual(response_data['request'], data)


    @httpretty.activate
    def test_request_with_url_image(self):
        image_url = 'http://test.com/test_image.jpg'
        mock_image_response(image_url, 'test/data/marmot.jpg')

        data = {
            'image': {
                'url': image_url
            }
        }
        resp = self.client.post(path='/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        response_data = json.loads(resp.get_data(as_text=True))
        self.assertEqual(response_data['image'], {
            'width': 183,
            'height': 275
        })


    @httpretty.activate
    def test_request_with_url_image_wrong(self):
        wrong_image_url = 'http://test.com/wrong_image.jpg'
        mock_error_response(wrong_image_url)

        data = {
            'image': {
                'url': wrong_image_url
            }
        }
        resp = self.client.post(path='/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        response_data = json.loads(resp.get_data(as_text=True))
        self.assertEqual(response_data['image'], False)
