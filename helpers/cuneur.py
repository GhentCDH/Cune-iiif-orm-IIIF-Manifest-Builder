import json
from typing import TypedDict

import helpers.svg as svg

class SignData(TypedDict):
    id: str
    transliteration: str
    line_index: int|None
    char_index: int|None
    word_index: int|None
    side: str
    points: list|None

type SignAnnotationList = list[SignData]

def parse_cuneur_annotations(filename: str) -> SignAnnotationList:
    signs: SignAnnotationList = []

    with open(filename) as source_file:
        annotations = json.load(source_file)
        for annotation in annotations.values():
            # get annotation info
            sign_data = {}
            sign_data['id'] = annotation['id'][1:]
            if annotation.get('target', {}).get('selector', {}).get('value', None):
                sign_data['points'] = svg.polygon_to_points(annotation['target']['selector']['value'])
            for body in annotation['body']:
                match body['purpose']:
                    case "Transliteration":
                        sign_data['transliteration'] = str(body['value']) if body.get('value') else None
                    case "Line":
                        sign_data['line_index'] = int(body['value']) if body.get('value') else None
                    case "Charindex":
                        sign_data['char_index'] = int(body['value']) if body.get('value') else None
                    case "Wordindex":
                        sign_data['word_index'] = int(body['value']) if body.get('value') else None
                    case "TabletSide":
                        sign_data['side'] = str(body['value']) if body.get('value') else None

            # skip invalid annotations
            required_keys = ['id', 'transliteration', 'line_index', 'char_index', 'side', 'points']
            if not all([key in sign_data.keys() for key in required_keys]):
                print(f"Invalid annotation: {sign_data}")
                continue

            # correct annotation info           
            sign_data['side'] = sign_data['side'].replace('front','obverse').replace('back','reverse')

            # add annotation to list
            signs.append(SignData(**sign_data))
    return signs