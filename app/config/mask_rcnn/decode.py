import base64
import numpy as np

from config.mask_rcnn.inference.config import Config
from config.mask_rcnn.inference.forward_model import ForwardModel

import json

# Your Inference Config Class
# Replace your own config
# MY_INFERENCE_CONFIG = YOUR_CONFIG_CLASS

class LocalConfig(Config):
    # Give the configuration a recognizable name
    NAME = "shapes"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    #IMAGES_PER_GPU = 1

    IMAGE_MIN_DIM = 512
    IMAGE_MAX_DIM = 512

    TRAIN_ROIS_PER_IMAGE = 32

    # Uncomment to train on 8 GPUs (default is 1)
    # GPU_COUNT = 8

    # Number of classes (including background)
    NUM_CLASSES = 15 
    MASK_SHAPE = [28, 28]


def decoder(result, parser, path):
    '''
    return pipeline request-data with image as three shaped list
    '''

    model_config = LocalConfig()
    preprocess_obj = ForwardModel(model_config)

    images = np.expand_dims(parser.image, axis=0)
    molded_images, image_metas, windows = preprocess_obj.mold_inputs(images)
    molded_images = molded_images.astype(np.float32)
    image_shape = molded_images[0].shape
    image_metas = image_metas.astype(np.float32)

    anchors = preprocess_obj.get_anchors(image_shape)
    anchors = np.broadcast_to(anchors, (images.shape[0],) + anchors.shape)
    data = preprocess_obj.result_to_dict(images, molded_images, windows, result['response'])

    return data



