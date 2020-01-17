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


    def json_connection(self, data, step):
        response = False
        headers = { "content-type": "application/json" }

        json_string=json.dumps(data)
        # size of json request data
        #print(len(json_string.encode('utf-8')))
        step_version = 1
        
        if 'version' in step:
            step_version = step['version']
        
        try:
            response = requests.post(self.model_url(step['model'], step_version), data=json_string, headers=headers)
            response_data = json.loads(response.text)
        
        except:
            
            if response:
                msg = response.text[:1000]
            else:
                msg = 'request failed'
            
            response_data = { 'error': { 'msg': msg } }

        return response_data


    def gprc_connection(self, data, step):
        '''
        inspired by https://github.com/bendangnuksung/mrcnn_serving_ready
        '''
        import grpc
        import tensorflow as tf
        from tensorflow_serving.apis import prediction_service_pb2_grpc
        from tensorflow_serving.apis import predict_pb2

        host = 'models'
        port = '8500'
        message_length = 4096 * 4096 * 3 # Max LENGTH the GRPC should handle
        channel = grpc.insecure_channel(str(host) + ':' + str(port), options=[('grpc.max_receive_message_length', message_length)])
        model_name = 'general_segmenter'
        signature_name = 'serving_default'

        channel = grpc.insecure_channel(str(host) + ':' + str(port), options=[('grpc.max_receive_message_length', message_length)])
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name
        request.model_spec.signature_name = signature_name
        
        for key, value in data.items():
            request.inputs[key].CopyFrom(value)

        result = {
            'response': stub.Predict(request, 60.)
        }
        return result


    def execute(self, step, path=[]):
        '''
        execute step actions
        '''
        response_data = False
        data = {}
        if 'encoder' in step:
            # IMPORTANT
            # execute external step function when available
            if callable(step['encoder']):
                data = step['encoder'](parser=self, path=path)
            elif 'name' in step['encoder'] and 'params' in step['encoder']:
                data = step['encoder']['name'](parser=self, path=path, params=step['encoder']['params'])


        #response_data = self.json_connection(data, step)
        response_data = self.gprc_connection(data, step)

        if 'error' not in response_data and 'decoder' in step:
            # IMPORTANT
            # execute external step function when available
            if callable(step['decoder']):
                response_data = step['decoder'](response_data, parser=self, path=path)
            elif 'name' in step['decoder'] and 'params' in step['decoder']:
                response_data = step['decoder']['name'](response_data, parser=self, path=path, params=step['decoder']['params'])
            
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


    def get_result_for_path(self, path):
        '''
        parse result data of n(path) steps and return result
        '''
        ret = self.data
        for path_step in path:
            if path_step is not 'next' and path_step in ret:
                ret = ret[path_step]
            else:
                ret = ret['result']
        return ret


    def process(self, step_names=False, path=[]):
        '''
        go through all steps and collect results
        '''
        if not step_names:
            step_names = self.config.start()

        for step_name in step_names:
            valid_step_name = False
            
            if type(step_name) is str:
                valid_step_name = step_name
            else:
                data = self.get_result_for_path(path)
                
                # compare the whole result
                if data == step_name['case']:
                    valid_step_name = step_name['model']
                
                # compare one element in list
                elif type(step_name['case']) is list:
                    valid_step_name = step_name['model']
                    if type(data) is list:
                        for index, case_step in enumerate(step_name['case']):
                            if type(data) is list and case_step is not None and case_step != data[index]:
                                valid_step_name = False
                    else:
                        for index, case_result in enumerate(step_name['case']):
                            if case_result is not None and case_result != data:
                                valid_step_name = False
            
                # compare one or more keys in dict
                elif type(step_name['case']) is dict and type(data) is dict:

                    checks = []
                    for key, value in step_name['case'].items():
                        # values are equal
                        if key in data.keys() and data[key] == value:
                            checks.append(True)
                        else:
                            checks.append(False)

                    # ALL checks are TRUE
                    if all(check == True for check in checks):
                        valid_step_name = step_name['model']

                # no matchin', go next
                else:
                    None
            
            if valid_step_name is not False:
                step = self.config.get(valid_step_name)
                if not step:
                    continue

                new_path = path + [valid_step_name]
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