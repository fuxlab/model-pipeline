from flask import Flask
from flask_restful import Resource, Api

from views.home import HomeView
from views.pipeline import PipelineView

import config
from parse.config import Config

app = Flask(__name__)
api = Api(app)

api.add_resource(HomeView, '/')
api.add_resource(PipelineView, '/')

#step_definitions = StepDefinitions(Config())

if __name__ == '__main__':
    
    app.run(
        host= '0.0.0.0',
        debug=True,
        port=8080
    )