

from helpers.iiif_uri import IfffUri
from helpers.resources import ImageDetails
from iiif_prezi3 import AnnotationBody, Canvas, Annotation, AnnotationPage, Choice

def create_image_resource_item(image: ImageDetails, iiif_uri: IfffUri, _config: dict) -> AnnotationBody:
    # image id
    image_id = _config["image_id_prefix"] + iiif_uri.id_from_file(image["file_path"])
    
    # create resource item
    resource_id = iiif_uri.create_image_uri(image_id)
    resource_item = AnnotationBody(id=resource_id,
                            type="Image",
                            format="image/jpeg",
                            width=image["width"],
                            height=image["height"],
                            service=[
                                {
                                    "id": iiif_uri.create_image_service_uri(image_id),
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
    choice_items: list[AnnotationBody], 
    uri_helper: IfffUri) -> Canvas:
    
    canvas_uri = uri_helper.create_canvas_uri(manifest_id, canvas_id)

    # get max width and height of images
    max_width = max([item.width for item in choice_items])
    max_height = max([item.height for item in choice_items])
    # create single canvas with choice
    # use manifest label as canvas label   
    
    canvas = Canvas(
        id=canvas_uri, # type: ignore
        label={"en": [canvas_label]}, # type: ignore
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
                        body = Choice(items=choice_items),
                        target=canvas_uri # type: ignore
                    )
                ],
                **{"@context": None}
            )                
        ],
        thumbnail = [ choice_items[0] ]
    )
    
    return canvas