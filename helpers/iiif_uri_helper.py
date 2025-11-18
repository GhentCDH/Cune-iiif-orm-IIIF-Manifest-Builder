import re
import os
from urllib import parse

class IfffUriHelper():
    IMAGE_SCHEME = "{base_url}/images/{image_id}/{region}/{size}/{rotation}/{quality}.{format}"
    IMAGE_SERVICE_SCHEME = "{base_url}/images/{image_id}"

    COLLECTION_SCHEME = "{base_url}/collections/{collection_id}"
    MANIFEST_SCHEME = "{base_url}/manifests/{manifest_id}"
    CANVAS_SCHEME = "{base_url}/manifests/{manifest_id}/canvas/{canvas_id}"
    SERVICE_SCHEME = "{base_url}/services/{service_id}/{id}"
    MANIFEST_DATA_SCHEME = "{base_url}/manifests/{manifest_id}/data/{data_id}"

    def __init__(self, base_url, base_path):
        self.base_url = base_url.rstrip('/')
        self.base_path = base_path.rstrip('/')

    def create_manifest_uri(self, manifest_id: str):
        return self.MANIFEST_SCHEME.format(base_url=self.base_url, manifest_id=manifest_id)

    def create_collection_uri(self, collection_id: str):
        return self.COLLECTION_SCHEME.format(base_url=self.base_url, collection_id=collection_id)

    def create_canvas_uri(self, manifest_id, canvas_id: str):
        return self.CANVAS_SCHEME.format(base_url=self.base_url, manifest_id=manifest_id, canvas_id=canvas_id)

    def create_image_uri(self, image_id: str, region: str ='full', size: str ='full', rotation: int = 0, quality: str = 'default', format: str = 'jpg'):
        return self.IMAGE_SCHEME.format(base_url=self.base_url, image_id=image_id, region=region, size=size, rotation=rotation, quality=quality, format=format)

    def create_image_service_uri(self, image_id: str):
        return self.IMAGE_SERVICE_SCHEME.format(base_url=self.base_url, image_id=image_id)
    
    def create_canvas_annotation_page_uri(self, manifest_id: str, canvas_id: str, annotation_page_id: str):
        return f"{self.create_canvas_uri(manifest_id, canvas_id)}/annotation-page/{annotation_page_id}"
    
    def create_canvas_annotation_uri(self, manifest_id: str, canvas_id: str, annotation_id: str):
        return f"{self.create_canvas_uri(manifest_id, canvas_id)}/annotation/{annotation_id}"
    
    def create_manifest_annotation_page_uri(self, manifest_id: str, annotation_page_id: str):
        return f"{self.create_manifest_uri(manifest_id)}/annotation-page/{annotation_page_id}"

    def create_manifest_annotation_uri(self, manifest_id: str, annotation_id: str):
        return f"{self.create_manifest_uri(manifest_id)}/annotation/{annotation_id}"
    
    def create_manifest_data_uri(self, manifest_id: str, data_id: str):
        return self.MANIFEST_DATA_SCHEME.format(base_url=self.base_url, manifest_id=manifest_id, data_id=data_id)
    
    def create_service_uri(self, object_id, service_id):
        return self.SERVICE_SCHEME.format(base_url=self.base_url, service_id=service_id, id=object_id)

    # Path methods
    def create_manifest_path(self, manifest_id: str):
        return os.path.join(self.base_path, self.id_to_path(manifest_id))

    def create_collection_path(self, collection_id: str):
        return os.path.join(self.base_path, self.id_to_path(collection_id))

    # def create_canvas_path(self, manifest_id: str, canvas_id: str):
    #     manifest_path = self.id_to_path(manifest_id)
    #     canvas_path = self.id_to_path(canvas_id)
    #     return os.path.join(self.base_path, manifest_path, "canvas", canvas_path)

    # def create_canvas_annotation_page_path(self, manifest_id: str, canvas_id: str, annotation_page_id: str):
    #     canvas_path = self.create_canvas_path(manifest_id, canvas_id)
    #     annotation_page_path = self.id_to_path(annotation_page_id)
    #     return os.path.join(canvas_path, "annotation-page", annotation_page_path)
    
    # def create_canvas_annotation_path(self, manifest_id: str, canvas_id: str, annotation_id: str):
    #     canvas_path = self.create_canvas_path(manifest_id, canvas_id)
    #     annotation_path = self.id_to_path(annotation_id)
    #     return os.path.join(canvas_path, "annotation", annotation_path)
    
    def create_manifest_annotation_page_path(self, manifest_id: str, annotation_page_id: str):
        manifest_path = self.create_manifest_path(manifest_id)
        annotation_page_path = self.id_to_path(annotation_page_id)
        return os.path.join(manifest_path, "annotation-page", annotation_page_path)

    def create_manifest_annotation_path(self, manifest_id: str, annotation_id: str):
        manifest_path = self.create_manifest_path(manifest_id)
        annotation_path = self.id_to_path(annotation_id)
        return os.path.join(manifest_path, "annotation", annotation_path)
    
    def create_manifest_data_path(self, manifest_id: str, data_id: str):
        manifest_path = self.id_to_path(manifest_id)
        data_path = self.id_to_path(data_id)
        return os.path.join(self.base_path, manifest_path, "data", data_path)

    def id_from_file(self, file_path: str) -> str:
        filename = os.path.basename(file_path)
        return self.id_from_path(file_path) + ':' + self.if_from_filename(filename)

    def id_from_path(self, path: str) -> str:
        path = os.path.dirname(path)
        path = path.replace(self.base_path, '')
        path = path.strip('/')
        return path.replace('/', ':')

    def if_from_filename(self, filename: str) -> str:
        return filename[:filename.rfind('.')]

    def id_to_path(self, id) -> str:
        id = id.replace(':', '/')
        # id = re.sub('#/[.]+/?#', '/', id)
        return id.strip('/')