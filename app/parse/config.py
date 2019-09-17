class Config:
    '''
    reading and parsing configuration
    '''

    def __init__(self, step_definition = []):
        
        self.identifier = 'model'

        self.step_definition = step_definition
        self.step_keys = [s[self.identifier] for s in self.step_definition]
        self.msg = []


    def start(self):
        '''
        get start entries
        '''
        steps = []
        for step in self.step_definition:
            if 'start' in step.keys() and step['start'] is True:
                if step[self.identifier] in self.step_keys:
                    steps.append(step[self.identifier])
        return steps


    def get(self, step_name):
        '''
        get full step
        '''
        if step_name in self.step_keys:
            for step in self.step_definition:
                if self.identifier in step.keys() and step[self.identifier] == step_name:
                    return step

        return False
    

    def validate(self):
        '''
        validate step_definition
        '''
        if len(self.start()) is 0:
            self.msg.append('start is missing')
            
        next_steps = []
        for step in self.step_definition:
            if 'next' in step and len(step['next']) > 0:
                for next_step in step['next']:
                    if type(next_step) is not str:
                        if 'model' not in next_step:
                            self.msg.append('model key missing for %s' % (step))
                        else:
                            if not self.get(next_step['model']):                            
                                self.msg.append('next step %s from %s not found.' % (step, next_step['model']))
                    elif not self.get(next_step):
                        self.msg.append('next step %s from %s not found.' % (step, next_step))

        if len(self.msg) == 0:
            return True
        return False
