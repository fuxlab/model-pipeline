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
        self.assertEqual(start, [])


    def test_config_start(self):      
        step_definition = [
            { 'model': 'step1' },
            { 'model': 'step2', 'start': True },
        ]
        
        config = Config(step_definition)
        self.assertEqual(config.start(), ['step2'])


    def test_config_start_invalid(self):
        step_definition = [
            { 'model': 'step1' },
            { 'model': 'step2' },
        ]
        
        config = Config(step_definition)
        self.assertEqual(config.start(), [])


    def test_config_get(self):
        step_definition = [
            { 'model': 'step1' },
            { 'model': 'step2', 'start': True },
        ]
        
        config = Config(step_definition)
        self.assertEqual(config.get('step2'), { 'model': 'step2', 'start': True })


    def test_next_single(self):
        step_definition = [
            { 'model': 'step1' },
            { 'model': 'step2', 'start': True, 'next': [ 'step3' ] },
            { 'model': 'step3' },
        ]
        config = Config(step_definition)
        self.assertEqual(config.next('step2'), [ 'step3' ] )


    def test_next_single_invalid(self):
        step_definition = [
            { 'model': 'step1' },
            { 'model': 'step2', 'start': True, 'next': [ 'step3' ] }
        ]
        config = Config(step_definition)
        self.assertEqual(config.next('step2'), [] )

    def test_next_multi(self):
        step_definition = [
            { 'model': 'step1' },
            { 'model': 'step2', 'start': True, 'next': [ 'step3', 'step4' ] },
            { 'model': 'step3' },
            { 'model': 'step4' },
        ]
        config = Config(step_definition)
        self.assertEqual(config.next('step2'), [ 'step3', 'step4' ] )

