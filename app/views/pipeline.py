from flask_restful import Resource
from flask_restful import reqparse

import config

class PipelineView(Resource):
    

    def post(self):
        '''
        '''
        parser = reqparse.RequestParser()
        args = parser.parse_args()

        return {
            'result': False,
            'params': args
        }

