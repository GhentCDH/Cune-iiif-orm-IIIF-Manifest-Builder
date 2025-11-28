import os
from PIL import Image
from typing import TypedDict


class ImageDetails(TypedDict):
    file_path: str
    width: int
    height: int


# get subfolders
def get_subfolders(path: str) -> list:   
    dirs = [os.path.join(path, filename) for filename in os.listdir(path) if os.path.isdir(os.path.join(path, filename)) and os.path.exists(os.path.join(path, filename, f"{filename}-annotator-annotations.json"))]
    return dirs

# find images in folder
def get_folder_images(path: str) -> list[ImageDetails]:
    images: list = []
    
    dirlist = os.listdir(path)
    dirlist.sort()
    
    image_filenames = [filename for filename in dirlist if os.path.isfile(os.path.join(path, filename)) and (filename.endswith('.jp2') or filename.endswith('.ptif'))]
    for filename in image_filenames:
        # Get the full file path
        file_path = os.path.join(path, filename)

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

