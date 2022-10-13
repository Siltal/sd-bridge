import json
from typing import Tuple, Any

import requests

server = '192.168.8.100:7860'


def predict(prompt, opt=False, neg='', step=20, seed=-1, width=512, height=832, cfg=7) -> Tuple[Any, str]:
    if opt is not False:
        neg += "Lowres,bad anatomy,bad hands,text,error,missing,fingers,extradigit,fewer digits,cropped,"
        "worst,quality,Low quality,normal quality,jpeg,artifacts,signature,watermark,username,blurry,"
        "badfeet"

    json_data = {
        'fn_index': 11,
        'data': [
            prompt+" ,{{{{{{{{{{{{{sfw}}}}}}}}}}}}}",
            neg,
            'None',
            'None',
            int(step),
            'Euler a',
            False,
            False,
            1,
            1,
            int(cfg),
            int(seed),
            -1,
            0,
            0,
            0,
            False,
            int(height),
            int(width),
            False,
            False,
            0.7,
            'None',
            False,
            False,
            None,
            '',
            'Seed',
            '',
            'Steps',
            '',
            True,
            False,
            None,
        ],
        'session_hash': '11451419198',
    }
    response = requests.post(f'http://{server}/api/predict/', json=json_data)
    data = json.loads(response.text)['data']
    seed: str = json.loads(data[1])['seed']
    print(seed)

    img_b64 = data[0][0][22:]
    return img_b64, seed


def img2img(img_b64, prompt='', opt=False, neg='', step=20, height=512, width=512, cfg=7, seed=-1, sc='R',
            dn=0.5):
    if opt is not False:
        neg += "Lowres,bad anatomy,bad hands,text,error,missing,fingers,extradigit,fewer digits,cropped,"
        "worst,quality,Low quality,normal quality,jpeg,artifacts,signature,watermark,username,blurry,"
        "badfeet"

    json_data = {
        'fn_index': 29,
        'data': [
            0,
            prompt+" ,{{{{{{{{{{{{{sfw}}}}}}}}}}}}}",
            neg,
            'None',
            'None',
            img_b64,
            None,
            None,
            None,
            'Draw mask',
            int(step),
            'DDIM',
            4,
            'original',
            False,
            False,
            1,
            1,
            int(cfg),
            float(dn),
            int(seed),
            -1,
            0,
            0,
            0,
            False,
            int(height),
            int(width),
            {
                'R': 'Just resize',
                'C': 'Crop and resize',
                'F': 'Resize and fill'
            }
            .get(sc.strip())
            ,
            False,
            32,
            'Inpaint masked',
            '',
            '',
            'None',
            '',
            '',
            1,
            50,
            0,
            False,
            4,
            1,
            '<p style="margin-bottom:0.75em">Recommended settings: Sampling Steps: 80-100, Sampler: Euler a, Denoising strength: 0.8</p>',
            128,
            8,
            [
                'left',
                'right',
                'up',
                'down',
            ],
            1,
            0.05,
            128,
            4,
            'fill',
            [
                'left',
                'right',
                'up',
                'down',
            ],
            False,
            False,
            None,
            '',
            '<p style="margin-bottom:0.75em">Will upscale the image to twice the dimensions; use width and height sliders to set tile size</p>',
            64,
            'None',
            'Seed',
            '',
            'Steps',
            '',
            True,
            False,
            None,
        ],
        'session_hash': '11451419198',
    }

    response = requests.post(f'http://{server}/api/predict/', json=json_data)
    print(response.text)
    data = json.loads(response.text)['data']
    seed: str = json.loads(data[1])['seed']
    img_b64 = data[0][0][22:]
    return img_b64, seed


def interrupt():
    json_data = {
        'fn_index': 0,
        'data': [],
        'session_hash': '11451419198',
    }
    requests.post(f'http://{server}/api/predict/', json=json_data)
