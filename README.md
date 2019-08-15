# Model-Pipeline

lorem ipsum dolot sit se amet

## Models

create a tensorflow serving configuration file under ./models/models.config:

    https://github.com/tensorflow/serving/blob/master/tensorflow_serving/g3doc/serving_config.md

For ssd_mobilenet_v1_coco_2018_01_28 it could look liḱe:

    model_config_list: {
        config: {
            name:  "ssd_mobilenet_v1_coco_2018_01_28",
            base_path:  "/models/ssd_mobilenet_v1_coco_2018_01_28",
            model_platform: "tensorflow"
        }
    }


Some Models to use out of the box:
- https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md


## Step Configuration:

Keys:

* version: None = latest
* model: Name of the model, defined in models.config
* input: image | text
* output: original | box_cropped | segmentation_cropped
* next_steps: list of next models


Example step definitions:

     'start': 1,
        'model': 'ssd_mobilenet_v1_coco_2018_01_28',
        'imput': 'image',
        'next_steps': [
            {
                'model': 'detection_garment',
                'version': 1
            },
        ]

## Endpoints / Requests

get results:

    POST / -D {
        url: 'https://pathtofile.com/file.jpg'
    }


get results at step x:

    POST / -D {
        url: 'https://pathtofile.com/file.jpg',
        detection_human: {
            value: 'male'
        }
    }


## Code:

run tests:

    docker-compose run api python -m unittest



Inspirations:

- https://www.tensorflow.org/tfx/serving/docker
- https://towardsdatascience.com/deploying-keras-models-using-tensorflow-serving-and-flask-508ba00f1037