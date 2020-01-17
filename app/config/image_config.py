import base64
import numpy as np
from io import BytesIO

def encode_base64(parser=None, path=[], params={}):
    '''
    return pipeline request-data with image encoded in b64
    https://stackoverflow.com/questions/51432589/how-do-i-get-a-tensorflow-keras-model-that-takes-images-as-input-to-serve-predic?noredirect=1&lq=1
    '''
    pimage = parser.image
    pimage = pimage.resize((300,300)) # Resize image to 300x300 and convert image

    if pimage.mode != 'RGB':
        pimage = pimage.convert('RGB')

    buffered = BytesIO()
    pimage.save(buffered, format="JPEG")
    input_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

    #encoded_input_string = base64.b64encode(pimage.read())
    #input_string = encoded_input_string.decode("utf-8")

    data = {
        'instances': [
            {'image_bytes': { 'b64': input_string }}
        ]
    }
    return data


def decode(outpt, parser=None, path=[], params={}):
    '''
    decode predictions from normal ssd
    '''
    pimage = parser.image
    y_pred = np.array(outpt['outputs'])

    confidence_threshold = 0.5
    y_pred = [y_pred[k][y_pred[k,:,1] > confidence_threshold] for k in range(y_pred.shape[0])]
    y_pred = y_pred[0].tolist()

    if 'classes' in params:
        for i in range(0, len(y_pred)):
            y_pred[i][0] = params['classes'][int(y_pred[i][0])]

    return y_pred