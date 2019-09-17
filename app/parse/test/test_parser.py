import json, warnings
import unittest, httpretty

from test.lib.mock_requests import mock_model_response
from PIL import Image

from api import app
from parse.config import Config
from parse.parser import Parser

class TestParser(unittest.TestCase):


    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed*")
        self.image = Image.open('test/data/marmot.jpg')


    def test_insert_at_path_empty(self):
        step_definition = []
        config = Config(step_definition)
        parser = Parser(config, data={})
        result = parser.insert_at_path(['a', 'b', 'c'], ['value'])
        self.assertEqual(parser.data, {
            'a': {
                'b': {
                    'c': ['value']
                }
            }
        })

    def test_insert_at_path_extend(self):
        step_definition = []
        config = Config(step_definition)
        parser = Parser(config, data={'a' : { 'a1': ['value1'] }})
        result = parser.insert_at_path(['a', 'b', 'c'], ['value'] )
        self.assertEqual(parser.data, {
            'a': {
                'b': {
                    'c': ['value']
                },
                'a1': ['value1']
            }
        })


    def test_empty(self):
        '''
        no step_definitions but image input data
        '''
        step_definition = [
        ]

        parser = Parser(Config(step_definition),
            model_endpoint=app.config['model_endpoint'],
            version=app.config['version'],
            data={
                'image': {
                    'width': self.image.width,
                    'height': self.image.height,
                }
            }
        )
        result = parser.process()

        expected_result = {
            'image': {
                'width': 183,
                'height': 275
            }
        }

        self.assertEqual(result, expected_result)


    @httpretty.activate
    def test_start(self):
        '''
        there are two start options
        '''
        step_definition = [
            { 'model': 'step1', 'start': True },
            { 'model': 'step2' },
        ]

        mock_model_response({
            'step1': { 'key1': 'value1' }
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': { 'key1': 'value1' }
            }
        }
        self.assertEqual(parser.data, expected_result)


    @httpretty.activate
    def test_double_start(self):
        '''
        there are two start options
        '''
        step_definition = [
            { 'model': 'step1', 'start': True },
            { 'model': 'step2', 'start': True },
            { 'model': 'step3' },
        ]

        mock_model_response({
            'step1': { 'key1': 'result1' },
            'step2': { 'key2': 'result2' },
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': { 'key1': 'result1' }
            },
            'step2': {
                'result': { 'key2': 'result2' }
            },
        }
        self.assertEqual(parser.data, expected_result)


    @httpretty.activate
    def test_double_follower(self):
        '''
        there are two start options
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [ 'step2', 'step3'] },
            { 'model': 'step2' },
            { 'model': 'step3' },
        ]

        mock_model_response({
            'step1': { 'key1': 'result1' },
            'step2': { 'key2': 'result2' },
            'step3': { 'key3': 'result3' },
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': { 'key1': 'result1' },
                'next': {
                    'step2': {
                        'result': { 'key2': 'result2' }
                    },
                    'step3': {
                        'result': { 'key3': 'result3' }
                    },
                }
            }
        }

        self.assertEqual(parser.data, expected_result)


    @httpretty.activate
    def test_splitting(self):
        '''
        one model gives more than one result that each needs to be processed further single
        when result is a list, next steps can be splitted
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [ 'step2' ] },
            { 'model': 'step2' },
        ]

        mock_model_response({
            'step1': [ 'result1', 'result2' ],
            'step2': { 'key21': 'result21' }
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                0: {
                    'result': 'result1',
                    'next': {
                        'step2': {
                            'result': { 'key21': 'result21' }
                        }
                    }
                },
                1: {
                    'result': 'result2',
                    'next':  {
                        'step2': {
                            'result': { 'key21': 'result21' }
                        }
                    }
                }
            }
        }
        self.assertEqual(parser.data, expected_result)


    @httpretty.activate
    def test_three_dive(self):
        '''
        three step definitions 
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [ 'step2' ] },
            { 'model': 'step2', 'next': [ 'step3' ] },
            { 'model': 'step3' },
        ]

        mock_model_response({
            'step1': 'result1',
            'step2': 'result2',
            'step3': 'result3',
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': 'result1',
                'next': {
                    'step2':{
                        'result': 'result2',
                        'next': {
                            'step3':{
                                'result': 'result3'
                            }
                        }
                    }
                }
            }
        }
        self.assertEqual(parser.data, expected_result)
        
    
    @httpretty.activate
    def test_three_dive_split(self):
        '''
        three step definitions 
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [ 'step2' ] },
            { 'model': 'step2', 'next': [ 'step3' ] },
            { 'model': 'step3' },
        ]

        mock_model_response({
            'step1': 'result1',
            'step2': ['result21', 'result22'],
            'step3': 'result3',
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': 'result1',
                'next': {
                    'step2':{
                        0: {
                            'result': 'result21',
                            'next': {
                                'step3':{
                                    'result': 'result3'
                                }
                            }
                        },
                        1: {
                            'result': 'result22',
                            'next': {
                                'step3':{
                                    'result': 'result3'
                                }
                            }
                        }
                    }
                }
            }
        }
        self.assertEqual(parser.data, expected_result)
        

    @httpretty.activate
    def test_switch_default_case(self):
        '''
        three step definitions 
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [
                { 'model': 'step2', 'case': 'result1' },
                { 'model': 'step3', 'case': 'result2' }
            ]},
            { 'model': 'step2' },
            { 'model': 'step3' },
        ]

        mock_model_response({
            'step1': 'result1',
            'step2': 'result2',
            'step3': 'result3',
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': 'result1',
                'next': {
                    'step2':{
                        'result': 'result2',
                    }
                }
            }
        }
        self.assertEqual(parser.data, expected_result)
        

    @httpretty.activate
    def test_switch_case_with_key_value_one_matching(self):
        '''
        three step definitions 
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [
                { 'model': 'step2', 'case': { 'key1': 'value1' } },
                { 'model': 'step3', 'case': 'result2' }
            ]},
            { 'model': 'step2' }
        ]

        mock_model_response({
            'step1': {
                'key1': 'value1',
                'key2': 'value2'
            },
            'step2': 'result2',
            'step3': 'result3',
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': {
                    'key1': 'value1',
                    'key2': 'value2'
                },
                'next': {
                    'step2':{
                        'result': 'result2',
                    }
                }
            }
        }
        self.assertEqual(parser.data, expected_result)


    @httpretty.activate
    def test_switch_case_with_key_value_one_matching_and_one_missing(self):
        '''
        three step definitions 
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [
                { 'model': 'step2', 'case': { 'key1': 'value1', 'key2': 'value2wrong' } },
                { 'model': 'step3', 'case': 'result2' }
            ]},
            { 'model': 'step2' }
        ]

        mock_model_response({
            'step1': {
                'key1': 'value1',
                'key2': 'value2'
            },
            'step2': 'result2',
            'step3': 'result3',
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            }
        }
        self.assertEqual(parser.data, expected_result)


    @httpretty.activate
    def test_switch_case_with_key_value_key_missing(self):
        '''
        three step definitions 
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [
                { 'model': 'step2', 'case': { 'key3': 'value3' } },
                { 'model': 'step3', 'case': 'result2' }
            ]},
            { 'model': 'step2' }
        ]

        mock_model_response({
            'step1': {
                'key1': 'value1',
                'key2': 'value2'
            },
            'step2': 'result2',
            'step3': 'result3',
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                'result': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            }
        }
        self.assertEqual(parser.data, expected_result)


    @httpretty.activate
    def test_switch_case_with_value(self):
        '''
        three step definitions 
        '''
        step_definition = [
            { 'model': 'step1', 'start': True, 'next': [
                { 'model': 'step2', 'case': [ None, 'result'] },
                { 'model': 'step3', 'case': 'result2' }
            ]},
            { 'model': 'step2' },
            { 'model': 'step3' },
        ]

        mock_model_response({
            'step1': [ 'resultX', 'result', 'resultY' ],
            'step2': 'result2',
            'step3': 'result3',
        })
        
        parser = Parser(Config(step_definition), model_endpoint=app.config['model_endpoint'], version=app.config['version'], data={})
        parser.process()

        expected_result = {
            'step1': {
                0: {
                    'result': 'resultX'
                },
                1: {
                    'result': 'result',
                    'next': {
                        'step2':{
                            'result': 'result2',
                        }
                    }
                },
                2: {
                    'result': 'resultY'
                }
            }
        }
        self.assertEqual(parser.data, expected_result)
