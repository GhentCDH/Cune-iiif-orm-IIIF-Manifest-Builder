from iiif_prezi3 import Manifest, AnnotationPage, AnnotationPageRef, Annotation, ResourceItem, Choice, BodyItem, config, Canvas
import os
from pathlib import Path

import json
from typing import TypedDict

from helpers.annotations import convert_annotator_annotations, patch_annotation
from helpers.iiif_resources import create_canvas_with_choice, create_resource_item
from helpers.iiif_uri_helper import IfffUriHelper
from helpers.resources import scan_images, scan_manifests
from helpers.svg import fix_svg_polygon_selector

config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"

manifest_is_choice = True

# init uri
_config = {
    "base_url": "https://iiif.ghentcdh.ugent.be/iiif",
    "base_path": os.path.abspath('../testset/'),
    "image_api": {
        "type": "ImageService2",
        "profile": "level2",
        "max_width": 5000,
        "max_height": 5000
    },
    "image_id_prefix": "cune-iiif-orm:testset:",
    "manifest_id_prefix": "cune-iiif-orm:sde:",
    "presentation_api": {
        "add_images_as_choice": True
    }
}

base_path = _config['base_path']

uri_helper = IfffUriHelper(_config['base_url'], _config['base_path'])

# find manifest folders
manifests = scan_manifests(base_path)

# loop over manifests
for manifest_path in manifests:

    # init manifest
    manifest_id = _config["manifest_id_prefix"] + uri_helper.id_from_path(manifest_path + '/')
    print(f"Processing manifest: {manifest_id}")

    manifest = Manifest(
        # id=uri_helper.create_manifest_uri(manifest_id),
        id="https://iiif.ghentcdh.ugent.be/data/cune-iiif-orm/sde/O.0219/manifest.json",
        label="O.0219"
    )

    images = scan_images(manifest_path)
    resource_items: list[ResourceItem] = [create_resource_item(image, uri_helper, _config) for image in images]
        

    # choice? create single canvas, annotationpage, annotation with body choice target canvas, annotation contains image resource items
    canvases: list[Canvas] = []

    if len(resource_items):
        if _config['presentation_api']['add_images_as_choice']:
            # create single canvas with choice
            # use manifest label as canvas label
            canvas_id = '0001'
            canvas = create_canvas_with_choice(canvas_id, manifest.label, manifest_id, resource_items, uri_helper)
            
            # add canvas to result    
            canvases.append(canvas)        
            
            # add annotations?
            annotations_source_path = os.path.join(manifest_path, 'annotations_orig.json')
            annotations_dest_path = os.path.join(manifest_path, 'sign-annotations.json')
            if os.path.exists(annotations_source_path):
                
                scale_factor = max([canvas.width/_config['image_api']['max_width'], canvas.height/_config['image_api']['max_height']])

                # add referencing annotation page to manifest
                annotation_page_uri = f"https://iiif.ghentcdh.ugent.be/data/{manifest_id.replace(':','/')}/sign-annotations.json"
                annotation_page = AnnotationPageRef(
                    # id=uri_helper.create_canvas_annotation_page_uri(manifest_id, canvas_id, "sign-annotations"),
                    id=annotation_page_uri,
                    type="AnnotationPage",
                )
                canvas.annotations.append(annotation_page)
                
                # create referenced annotation page
                convert_annotator_annotations(
                    annotations_source_path,
                    annotations_dest_path,
                    annotation_page_uri,
                    canvas.id,
                    scale_factor,
                    lambda annotation_id: uri_helper.create_canvas_annotation_uri(manifest_id, canvas_id, annotation_id),
                )          

        if not manifest_is_choice:
            for index, image in enumerate(images):
                canvas_id = '0001'
                canvas_uri = uri_helper.create_canvas_uri(manifest_id, canvas_id)
                resource_item = image['resource_item']
                canvas = Canvas(
                    id=canvas_uri,
                    label=resource_item.label,
                    height=resource_item.height,
                    width=resource_item.width,
                    annotations=[],
                    items=[
                        AnnotationPage(
                            id=f"{canvas_uri}/annotation-page/images",
                            items=[
                                Annotation(
                                    id=f"{canvas_uri}/annotation/images/{index}", 
                                    motivation="painting",
                                    body = resource_item,
                                    target=canvas_uri
                                )
                            ]
                        )
                    ]
                )
                canvases.append(canvas)
                break
            
            # patch annotations?
            annotations_source_path = os.path.join(manifest_path, 'annotations_orig.json')
            annotation_page = AnnotationPage(id=f"{canvas_uri}/annotation-page/annotations", items=[])
            if os.path.exists(annotations_source_path):
                with open(annotations_source_path) as file:
                    annotations = json.load(file)
                    i = 0
                    for annotation_id, annotation in annotations.items():
                        annotation = patch_annotation(annotation, canvas_uri, uri_helper.create_canvas_annotation_uri(manifest_id, canvas_id, annotation_id))

                        # add annotations to manifest
                        annotation_page.items.append(annotation)
                        i += 1
                        if i == _config.get('max_annotations', None):
                            break

                    # output annotations
                    annotations_path_output = os.path.join(manifest_path, 'annotations.json')
                    with open(annotations_path_output, 'w') as file:
                        json.dump(annotations, file, indent=4)
                        
                    canvas.annotations.append(annotation_page)                   


    # add canvases to manifest
    manifest.items = canvases

    # output manifest
    with open(os.path.join(manifest_path, 'manifest.json'), 'w') as file:
        file.write(manifest.jsonld())






