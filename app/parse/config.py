import config

class Config:


    def __init__(self, step_definitions = []):
        self.step_definitions = step_definitions


    def start(self):
        '''
        '''
        for step in self.step_definitions:
            if 'start' in step and step['start'] is True:
                return step
        return False
