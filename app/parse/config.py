class Config:
    '''
    reading and parsing configuration
    '''

    def __init__(self, step_definition = []):
        
        self.identifier = 'model'

        self.step_definition = step_definition
        self.step_keys = [s[self.identifier] for s in self.step_definition]


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
    

    def next(self, step_name):
        '''
        get next steps of step
        '''
        next_steps = []
        step = self.get(step_name)
        if step_name and 'next' in step.keys():
            for next_step_name in step['next']:
                if next_step_name in self.step_keys:
                    next_steps.append(next_step_name)

        return next_steps
