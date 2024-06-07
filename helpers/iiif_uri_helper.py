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

    def create_service_uri(self, object_id, service_id):
        return self.SERVICE_SCHEME.format(base_url=self.base_url, service_id=service_id, id=object_id)

    # def createContentID(self, _manifest_id, _file_id):
    #     return f"{_manifest_id}:{_file_id}"

    # def getManifestPath(self, _manifest_id):
    #     return f"{self.base_path}/{self.IDtoPath(_manifest_id)}"

    # def getCollectionPath(self, _collection_id):
    #     return f"{self.base_path}/{self.IDtoPath(_collection_id)}"

    # def getIDFromRequestUri(self, _request_uri):
    #     base_path = parse.urlparse(self.base_url).path
    #     regexp = f"{base_path}/({self.collection_prefix}|{self.MANIFEST_PREFIX})/([.a-z0-9_-]+(:([.a-z0-9_-]+)+)*)"
    #     regexp = f";^{regexp}$;i"
    #     matches = re.match(regexp, _request_uri)
    #     if not matches:
    #         raise Exception('Invalid id')
    #     _id = matches.group(2)
    #     _id = re.sub('#:[.]+:?#', ':', _id)
    #     return _id

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
        id = re.sub('#/[.]+/?#', '/', id)
        return id.strip('/')