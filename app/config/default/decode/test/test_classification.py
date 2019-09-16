import json
import numpy as np
import unittest

from numpy.testing import assert_array_equal

from config.default.decode.classification import decode_classification

class TestDefaultsDecodeTestClassification(unittest.TestCase):


    def setUp(self):
        None


    def test_decode_classification(self):
        outpt = {
            'outputs': [
                [
                    0.1,
                    0.2,
                    0.3,
                    0.4,
                ]
            ]
        }
        params = {
            'classes': [
                'one',
                'two',
                'three',
                'four'
            ],
            'threshold': 0.3
        }
        
        result = decode_classification(outpt, parser=None, path=[], params=params)
        self.assertEqual(result, {
            'three': 0.3,
            'four': 0.4,
        })