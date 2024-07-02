

from helpers.iiif_uri_helper import IfffUriHelper
from helpers.resources import ImageDetails
from iiif_prezi3 import ResourceItem, Canvas, Annotation, AnnotationPage, Choice

def create_resource_item(image: ImageDetails, uri_helper: IfffUriHelper, _config: dict) -> ResourceItem:
    # image id
    image_id = _config["image_id_prefix"] + uri_helper.id_from_file(image["file_path"])
    
    # create resource item
    resource_id = uri_helper.create_image_uri(image_id)
    resource_item = ResourceItem(id=resource_id,
                            type="Image",
                            format="image/jpeg",
                            width=image["width"],
                            height=image["height"],
                            service=[
                                {
                                    "id": uri_helper.create_image_service_uri(image_id),
                                    "type": _config['image_api']['type'],
                                    "profile": _config['image_api']['profile']
                                }
                            ]
    )

    # create label from image_id
    resource_item.add_label(image_id.split('_')[-1]
                            .replace('Color', 'Color ')
                            .replace('Shaded', 'Shaded ')
                            .replace('Sketch', 'Sketch ')
                            .replace('01', '')
                            .replace('00', '')
                            , "en")
    
    return resource_item
    
def create_canvas_with_choice(
    canvas_id: str, 
    canvas_label: str,
    manifest_id: str, 
    resource_items: list[ResourceItem], 
    uri_helper: IfffUriHelper) -> Canvas:
    
    canvas_uri = uri_helper.create_canvas_uri(manifest_id, canvas_id)

    # get max width and height of images
    max_width = max([resource_item.width for resource_item in resource_items])
    max_height = max([resource_item.height for resource_item in resource_items])
    # create single canvas with choice
    # use manifest label as canvas label   
    
    canvas = Canvas(
        id=canvas_uri,
        label=canvas_label, 
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
                ]
            )                
        ]
    )
    
    return canvas