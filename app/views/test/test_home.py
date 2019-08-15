import json
import unittest

from api import app

class TestHome(unittest.TestCase):


    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    
    def test_home(self):

        resp = self.client.get(path='/')
        self.assertEqual(resp.status_code, 200)

