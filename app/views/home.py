from flask_restful import Resource
from config.config import VERSION

class HomeView(Resource):
    

    def get(self):
        '''
        root information endpoint
        '''
        return {
            'Visual Search Pipeline': 'v%s' % (VERSION)
        }

