from config.config import MODEL_ENDPOINT, VERSION
import json, requests
import numpy as np

from functools import reduce
import collections

class Parser:
    '''
    it does:
    make requests to models
    parse results
    '''

    def __init__(self, config, image=None, model_endpoint=None, version=None, data={}):
        self.config = config
        self.image = image
        self.version = version
        self.model_endpoint = model_endpoint
        self.data = data
        return None


    def model_url(self, model_name, model_version=1):
        # Todo: better use grpc - https://github.com/Vetal1977/tf_serving_flask_app/blob/master/api/gan/logic/tf_serving_client.py
        # Todo: use swagger
        return "%s/v%s/models/%s/versions/%s:predict" % (self.model_endpoint, self.version, model_name, model_version)


    def execute(self, step, path=[]):
        '''
        execute step actions
        '''
        response_data = False
        data = {}
        if 'encoder' in step:
            # IMPORTANT
            # execute external step function when available
            data = step['encoder'](parser=self, path=path)

        response = False
        try:
            headers = { "content-type": "application/json" }
            json_string=json.dumps(data)
            
            # size of json request data
            #print(len(json_string.encode('utf-8')))
            step_version = 1
            
            if 'version' in step:
                step_version = step['version']
            
            response = requests.post(self.model_url(step['model'], step_version), data=json_string, headers=headers)
            response_data = json.loads(response.text)

        except:
            if response:
                msg = response.text[:1000]
            else:
                msg = 'request failed'
            
            response_data = { 'error': { 'msg': msg } }
        
        if 'error' not in response_data and 'decoder' in step:
            # IMPORTANT
            # execute external step function when available
            response_data = step['decoder'](response_data, parser=self, path=path)
            
        return response_data


    def dict_merge(dct, merge_dct):
        for key, value in merge_dct.items():
            if key in dct and isinstance(dct[key], dict) and isinstance(merge_dct[key], collections.Mapping):
                Parser.dict_merge(dct[key], merge_dct[key])
            else:
                dct[key] = merge_dct[key]
    
    
    def insert_at_path(self, path, value={}):
        '''
        insert something at path
        '''
        elements = [value] + list(reversed(path))
        nested = reduce(lambda x, y: {y: x}, elements)
        Parser.dict_merge(self.data, nested)


    def process(self, step_names=False, path=[]):
        '''
        go through all steps and collect results
        '''
        if not step_names:
            step_names = self.config.start()

        for step_name in step_names:
            step = self.config.get(step_name)
            if not step:
                continue

            new_path = path + [step_name]
            results = self.execute(step, path)
            

            if isinstance(results, list):
                # many results => do processing for each
                index = 0
                for result in results:
                    self.insert_at_path(new_path + [index, 'result'], result)
                    if 'next' in step.keys() and  len(step['next']) > 0:
                        self.process(step_names=step['next'], path=new_path + [index, 'next'])
                    index += 1
            else:
                self.insert_at_path(new_path + ['result'], results)
                # one result => do processing once
                if 'next' in step.keys() and  len(step['next']) > 0:
                    self.process(step_names=step['next'], path=new_path + ['next'])
        
            
        
        return self.data