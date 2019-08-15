VERSION = 1

STEP_DEFINITIONS = [
    {
        'start': 1,
        'model': 'ssd_mobilenet_v1_coco_2018_01_28',
        'version': 1
        'imput': 'image',
        'next_steps': [
            {
                'model': 'detection_garment'
            },
        ]
    }
]