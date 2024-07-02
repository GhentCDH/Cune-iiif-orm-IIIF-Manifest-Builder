import json
import os
from helpers.svg import fix_svg_polygon_selector
from iiif_prezi3 import AnnotationPage

def patch_annotation(annotation: dict, canvas_uri: str, annotation_uri: str, scale_factor: float = 1.0):
    # patch target source
    annotation['target']['source'] = canvas_uri
    annotation['target']['type'] = "SpecificResource"
    # patch target svg selector (polygon -> path)
    annotation['target']['selector'] = fix_svg_polygon_selector(annotation['target']['selector'], scale_factor)

    # patch id/motivation/context
    annotation['id'] = annotation_uri
    annotation['motivation'] = "describing"
    del annotation['@context']
    return annotation

def convert_annotator_annotations(
    annotations_source_path: str,
    annotations_dest_path: str,
    annotation_page_uri: str,
    annotation_target_uri: str,
    scale_factor: float,
    annotation_uri_generator: callable) -> None:
    
    # create referenced annotation page
    annotation_page = AnnotationPage(
        # id=uri_helper.create_canvas_annotation_page_uri(manifest_id, canvas_id, "sign-annotations"),
        id=annotation_page_uri,
        items=[]
    )
    with open(annotations_source_path) as source_file:
        annotations = json.load(source_file)
        for annotation_id, annotation in annotations.items():
            annotation = patch_annotation(
                annotation, 
                annotation_target_uri, 
                annotation_uri_generator(annotation['id']),
                scale_factor)
            annotation_page.items.append(annotation)
            # todo: sort annotaitons by line/word/char
    # output annotations
    with open(annotations_dest_path, 'w') as dest_file:
        json.dump(annotation_page.jsonld_dict(), dest_file, indent=4)