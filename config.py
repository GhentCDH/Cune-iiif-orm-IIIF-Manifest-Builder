import os

_config = {
    "base_url": "https://iiif.ghentcdh.ugent.be/iiif",
    "base_path": os.path.abspath('/workspaces/data'),
    "image_api": {
        "type": "ImageService2",
        "profile": "level2",
        "max_width": 5000,
        "max_height": 5000
    },
    "image_id_prefix": "cune-iiif-orm:testset:",
    "manifest_id_prefix": "cune-iiif-orm:sde:",
    "collection_id": "cune-iiif-orm:sde",
    "verbose": False
}
