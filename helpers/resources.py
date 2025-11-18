import os
from PIL import Image
from typing import TypedDict


class ImageDetails(TypedDict):
    file_path: str
    width: int
    height: int


# find manifest folders
def scan_manifests(base_path: str) -> list:   
    dirs = [os.path.join(base_path, filename) for filename in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, filename)) and os.path.exists(os.path.join(base_path, filename, f"{filename}-annotator-annotations.json"))]
    return dirs

# find images in manifest
def scan_images(manifest_path: str) -> list[ImageDetails]:
    images: list = []
    
    dirlist = os.listdir(manifest_path)
    dirlist.sort()
    
    image_filenames = [filename for filename in dirlist if os.path.isfile(os.path.join(manifest_path, filename)) and (filename.endswith('.jp2') or filename.endswith('.ptif'))]
    for filename in image_filenames:
        # Get the full file path
        file_path = os.path.join(manifest_path, filename)

        # option 1: get with and height from image api
        # image_api_uri = uri_helper.create_image_service_uri(image_id)
                
        # option 2: get with and height form image
        image = Image.open(file_path)
        width, height = image.size
        
        # append image item
        images.append({
            "file_path": file_path,
            "width": width,
            "height": height,
        })
        
    return images

