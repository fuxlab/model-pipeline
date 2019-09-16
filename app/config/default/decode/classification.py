import numpy as np

def decode_classification(outpt, parser=None, path=[], params={}):
    '''
    '''
    if 'outputs' not in outpt:
        return []

    if 'classes' not in params:
        return outpt

    threshold = 0.8
    if 'threshold' in params:
        threshold = params['threshold']

    super_threshold_indices = np.array(outpt['outputs'][0]) >= threshold
    label_indicies = np.where(super_threshold_indices==True)
    labels = dict(zip(
        list(np.array(params['classes'])[label_indicies]),
        list(np.array(outpt['outputs'][0])[label_indicies])
    ))
    
    return labels