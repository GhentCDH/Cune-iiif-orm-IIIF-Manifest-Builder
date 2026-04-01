import json
from helpers.cuneur import SignData
import helpers.svg as svg

from iiif_prezi3 import AnnotationPage, Annotation, Base



def save_iiif_model(model: Base, dest_path: str):
    with open(dest_path, 'w') as dest_file:
        json.dump(model.jsonld_dict(), dest_file, indent=4)


def create_annotation_page(id: str, label: str, items: list[Annotation]) -> AnnotationPage:
    annotation_page = AnnotationPage(
        id=id, # type: ignore
        items=items,
        label={"en": [label]}, # type: ignore
        **{"@context": None}
    )

    return annotation_page
   
def create_sign_annotation(sign: SignData, annotation_uri: str, target_uri: str) -> Annotation:

    body = []

    signPosition = {}
    signPosition['side'] = sign.get('side')
    signPosition["lineIndex"] = sign.get("line_index")
    signPosition["wordIndex"] = sign.get("word_index")
    signPosition["charIndex"] = sign.get("char_index")

    if sign.get("transliteration"):
        body.append(
            {
                "type": "TextualBody",
                "purpose": "transliterating",
                "value": sign["transliteration"],
                "format": "text/plain"
            },            
        )

    body.append({
        "type": "SignPosition",
        **signPosition
    })

    annotation = Annotation(
        id = annotation_uri, # type: ignore
        motivation = "describing",
        body = body,
        target = [
            {
                "type": "SpecificResource",
                "source": target_uri,
                "selector": {
                    "type": "SvgSelector",
                    "value": svg.points_to_path(sign["points"])
                }
            }
        ]
    )
    return annotation

def create_translation_annotation(translation: str, annotation_uri: str, target_uri: str) -> Annotation:

    annotation = Annotation(
        id = annotation_uri, # type: ignore
        motivation = "describing",
        body=[
            {
                "type": "TextualBody",
                "value": translation,
                "format": "text/plain",
                "purpose": "translating",
                "language": "en",
            }
        ],
        target=[ target_uri ] # type: ignore
    )
    return annotation

def create_transliteration_annotation(transliteration: str, annotation_uri: str, target_uri: str) -> Annotation:

    annotation = Annotation(
        id = annotation_uri, # type: ignore
        motivation = "describing",
        body=[
            {
                "type": "TextualBody",
                "value": transliteration,
                "format": "text/x-atf",
                "purpose": "transliterating",
            }
        ],
        target=[ target_uri ] # type: ignore
    )
    return annotation


