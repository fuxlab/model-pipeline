import base64
import numpy as np

def encode_request_image(parser=None, path=[], params={}):
    '''
    return pipeline request-data with image as three shaped list
    '''
    pimage = parser.image
    pimage = pimage.resize(params['shape'])

    if pimage.mode != 'RGB':
        pimage = pimage.convert('RGB')

    image = np.array(pimage)
    fimage = image.astype(np.float32)
    image_data = fimage.tolist()
    
    data = { 'inputs': [ image_data ] }

    return data
