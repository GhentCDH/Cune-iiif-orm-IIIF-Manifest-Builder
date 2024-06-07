from iiif_prezi3 import Manifest, AnnotationPage, Annotation, ResourceItem, Choice, BodyItem, config, Canvas
import os
from pathlib import Path
from PIL import Image
import json

from helpers.iiif_uri_helper import IfffUriHelper
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
    }
}

base_path = _config['base_path']

uri_helper = IfffUriHelper(_config['base_url'], _config['base_path'])

# init prefixes
manifest_id_prefix = "cune-iiif-orm:sde:"
image_id_prefix = "cune-iiif-orm:testset:"

# init manifest
manifest_path = os.path.join(base_path, 'O.0219') + '/'
manifest_id = manifest_id_prefix + uri_helper.id_from_path(manifest_path)

manifest = Manifest(
    id=uri_helper.create_manifest_uri(manifest_id),
    label="O.0219"
)

# find images
images: list = []
resource_items: list[ResourceItem] = []
image_filenames = [filename for filename in os.listdir(manifest_path) if os.path.isfile(os.path.join(manifest_path, filename)) and (filename.endswith('.jp2') or filename.endswith('.ptif'))]
for filename in image_filenames:
    # Get the full file path
    file_path = os.path.join(manifest_path, filename)

    # option 1: get with and height from image api
    # image_api_uri = uri_helper.create_image_service_uri(image_id)
            
    # option 2: get with ahd height form image
    image = Image.open(file_path)
    width, height = image.size
    
    # image id
    image_id = image_id_prefix + uri_helper.id_from_file(file_path)
    
    # create resource item
    resource_id = uri_helper.create_image_uri(image_id)
    resource_item = ResourceItem(id=resource_id,
                            type="Image",
                            format="image/jpeg",
                            width=width,
                            height=height,
                            service=[
                                {
                                    "id": uri_helper.create_image_service_uri(image_id),
                                    "type": _config['image_api']['type'],
                                    "profile": _config['image_api']['profile']
                                }
                            ]
    )
    resource_item.add_label(image_id, "en")
    
    # append resource item
    resource_items.append(resource_item)
    
    # append image item
    images.append({
        "file_path": file_path,
        "width": width,
        "height": height,
        "resource_item": resource_item,
    })

# choice? create single canvas, annotationpage, annotation with body choice target canvas, annotation contains image resource items
canvases: list[Canvas] = []

if len(resource_items):
    if manifest_is_choice:
        # get max width and height of images
        max_width = max([resource_item.width for resource_item in resource_items])
        max_height = max([resource_item.height for resource_item in resource_items])
        # create single canvas with choice
        # use manifest label as canvas label
        canvas_id = "0001"
        canvas_uri = uri_helper.create_canvas_uri(manifest_id, canvas_id)
        canvas = Canvas(
            id=canvas_uri,
            label=manifest.label, 
            width=max_width,
            height=max_height,
            annotations=[],            
            items=[
                AnnotationPage(
                    id=uri_helper.create_canvas_annotation_page_uri(manifest_id, canvas_id, "layers"),
                    items=[
                        Annotation(
                            id=uri_helper.create_canvas_annotation_uri(manifest_id, canvas_id, "layers"),
                            motivation="painting",
                            body = Choice(items=resource_items),
                            target=canvas_uri
                        )
                    ],
                )
            ]
        )
        
        # patch annotations?
        scale_factor = max([canvas.width/_config['image_api']['max_width'], canvas.height/_config['image_api']['max_height']])
        print(scale_factor)
        annotations_path = os.path.join(manifest_path, 'annotations_orig.json')
        annotation_page = AnnotationPage(
            id=uri_helper.create_canvas_annotation_page_uri(manifest_id, canvas_id, "sign-annotations"),
            items=[]
        )
        if os.path.exists(annotations_path):
            with open(annotations_path) as file:
                annotations = json.load(file)
                i = 0
                for annotation_id, annotation in annotations.items():
                    # patch target source
                    annotation['target']['source'] = canvas_uri
                    annotation['target']['type'] = "SpecificResource"
                    # patch target svg selector (polygon -> path)
                    annotation['target']['selector'] = fix_svg_polygon_selector(annotation['target']['selector'], scale_factor)
                    
                    # patch id/motivation/context
                    annotation['id'] = f"{canvas_uri}/annotation/{annotation['id']}"
                    annotation['motivation'] = "tagging"
                    del annotation['@context']

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
                
        # add canvas to result    
        canvases.append(canvas)            

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
        annotations_path = os.path.join(manifest_path, 'annotations_orig.json')
        annotation_page = AnnotationPage(id=f"{canvas_uri}/annotation-page/annotations", items=[])
        if os.path.exists(annotations_path):
            with open(annotations_path) as file:
                annotations = json.load(file)
                i = 0
                for annotation_id, annotation in annotations.items():
                    # patch target source
                    annotation['target']['source'] = canvas_uri
                    annotation['target']['type'] = "SpecificResource"
                    # patch target svg selector (polygon -> path)
                    annotation['target']['selector'] = fix_svg_polygon_selector(annotation['target']['selector'])
                    
                    # patch id/motivation/context
                    annotation['id'] = f"{canvas_uri}/annotation/{annotation['id']}"
                    annotation['motivation'] = "tagging"
                    del annotation['@context']

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






