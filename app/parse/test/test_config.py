import json
import unittest

from parse.config import Config

class TestConfig(unittest.TestCase):

    def setUp(self):
        None

    
    def test_false_config_start(self):

        step_definition_without_start = [
            { 'model': 'step1' },
            { 'model': 'step2' },
        ]
        
        start = Config(step_definition_without_start).start()
        self.assertEqual(start, False)


    def test_config_start(self):      
        step_definition_with_start = [
            { 'model': 'step1' },
            { 'model': 'step2', 'start': True },
        ]
        
        start = Config(step_definition_with_start).start()
        self.assertEqual(start['model'], 'step2')        
