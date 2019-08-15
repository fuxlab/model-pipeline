import json
import unittest

from api import app

class TestPipeline(unittest.TestCase):


    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    
    def test_basic_steps(self):
        data = {}
        resp = self.client.post(path='/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
