from flask_restful import Resource
import config

class HomeView(Resource):
    

    def get(self):
        '''
        root information endpoint
        '''
        return {
            'Visual Search Pipeline': 'v%s' % (config.VERSION)
        }

