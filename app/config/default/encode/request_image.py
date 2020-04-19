import base64
import numpy as np
from io import BytesIO

from config.mask_rcnn.inference.forward_model import ForwardModel

class InferenceConfig():
    GPU_COUNT = 0
    IMAGES_PER_GPU = 0
    NAME = "coco"
    NUM_CLASSES = 15
    IMAGE_RESIZE_MODE = 'square'


def encode_request_image(parser=None, path=[], params={}):
    '''
    return pipeline request-data with image as three shaped list
    '''
    pimage = parser.image
    pimage = pimage.resize(params['shape'])

    if pimage.mode != 'RGB':
        pimage = pimage.convert('RGB')

    #image = np.array(pimage)
    #print(image)
    #fimage = image.astype(np.float32)
    #print(image.shape)
    #image_data = fimage.tolist()
    #print(image_data.shape)
    #print(len(image_data))
    #byte_io = BytesIO()

    #pimage.save(byte_io, 'PNG')

    model_config = InferenceConfig()
    image_shape = params['shape']

    preprocess_obj = ForwardModel(model_config)

    images = np.expand_dims(pimage, axis=0)
    molded_images, image_metas, windows = preprocess_obj.mold_inputs(images)
    molded_images = molded_images.astype(np.float32)
    image_metas = image_metas.astype(np.float32)

    anchors = preprocess_obj.get_anchors(image_shape)
    anchors = np.broadcast_to(anchors, (images.shape[0],) + anchors.shape)

    data = {
        'inputs': {
            'input_image': molded_images.tolist(),
            'input_image_meta': image_metas.tolist(),
            'input_anchors': anchors.tolist(),
        }
    }

    return data
