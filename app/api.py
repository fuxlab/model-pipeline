from flask import Flask
from flask_restful import Resource, Api

from views.home import HomeView
from views.pipeline import PipelineView

from config.config import STEP_DEFINITIONS,VERSION,MODEL_ENDPOINT
from parse.config import Config

app = Flask(__name__)
app.config['config'] = Config(STEP_DEFINITIONS)
app.config['version'] = VERSION
app.config['model_endpoint'] = MODEL_ENDPOINT

api = Api(app)
api.add_resource(HomeView, '/')
api.add_resource(PipelineView, '/')

if __name__ == '__main__':
    app.run(
        host= '0.0.0.0',
        debug=True,
        port=8080
    )