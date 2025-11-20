#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import shutil

from iiif_prezi3 import Manifest, AnnotationPageRefExtended, AnnotationBody, config, Canvas, LinkedResource, Collection, Annotation, ManifestRef

import helpers.annotations as annotations
import helpers.cuneur as cuneur
import helpers.svg as svg
from helpers.atf_indexer import AtfIndexer

from helpers.iiif_resources import create_canvas_with_choice, create_image_resource_item
from helpers.iiif_uri import IfffUri
from helpers.nodegoat_metadata import nodegoat_to_iiif_metadata
from helpers.resources import scan_images, scan_manifests
from config import _config

config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"

# init uri
base_path = _config['base_path']

# init url/path helper
iiif_uri = IfffUri(_config['base_url'], _config['base_path'])

# find manifest folders
manifests = scan_manifests(base_path)
# manifests = ['/workspaces/data/O.0219'] 

# create atf reader
atf_reader = AtfIndexer()

# create collection manifest
collection_manifest = Collection(id=iiif_uri.create_collection_uri(_config['collection_id']), label={"en": ["Cune-iiif-orm SDE"]},items=[], type="Collection") # type: ignore

# loop over manifests
for manifest_path in manifests:

    tablet_id = os.path.basename(manifest_path)

    print(f"Processing {tablet_id} ...")

    # clean previous exports
    print("- Cleaning previous exports ...")
    manifest_paths = [
        os.path.join(manifest_path, "manifest.json"),
        os.path.join(manifest_path, "sign-annotations.json"),
        os.path.join(manifest_path, "sign-annotations-new.json"),
        os.path.join(manifest_path, f"{tablet_id}-sign-annotations.json"),
        os.path.join(manifest_path, f"{tablet_id}-word-annotations.json"),
        os.path.join(manifest_path, f"{tablet_id}-line-annotations.json"),
        os.path.join(manifest_path, f"{tablet_id}-translation-annotations.json"),
        os.path.join(manifest_path, f"{tablet_id}-translations.json"),
        os.path.join(manifest_path, f"{tablet_id}-transliteration-annotations.json"),
        os.path.join(manifest_path, f"{tablet_id}-transliterations.json"),
    ]
    for path in manifest_paths:
        if os.path.exists(path):
            os.remove(path)

    # create annotation-page and annotation directory
    manifest_paths = {
        "annotation-page": os.path.join(manifest_path, "annotation-page"),
        "annotation": os.path.join(manifest_path, "annotation"),
        "data": os.path.join(manifest_path, "data")
    }

    # create and empty folders defined in paths
    print("- Create output directories ...")
    for key, path in manifest_paths.items():
        # create directory
        if not os.path.exists(path):
            os.mkdir(path)
        # empty directory
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # scan images
    images = scan_images(manifest_path)

    # load nodegoat data
    print("- Load nodegoat data ...")
    nodegoat_data = {}
    nodegoat_data_path = os.path.join(manifest_path, f"{tablet_id}-data.json")
    if os.path.exists(nodegoat_data_path):
        with open(nodegoat_data_path, 'r', encoding='utf-8') as f:
            nodegoat_data = json.load(f)

        # copy file to data folder
    else:
        print(f"- No nodegoat data found at {nodegoat_data_path}")

    # load transliteration
    print("- Load transliteration ...")
    transliteration_path = os.path.join(manifest_path, f"{tablet_id}-transliteration-atf.txt")
    transliteration_text = None
    if os.path.exists(transliteration_path):
        with open(transliteration_path, 'r', encoding='utf-8') as f:
            transliteration_text = f.read()
    else:
        print(f"- No transliteration found at {transliteration_path}")

    # Load translations
    print("- Load translation ...")
    translation_data_path = os.path.join(manifest_path, f"{tablet_id}-translation.txt")
    if os.path.exists(translation_data_path):
        translation_text = open(translation_data_path, 'r', encoding='utf-8').read()
    else:
        print(f"- No translation found at {translation_data_path}")

    # load sign annotations
    print("- Load sign annotations ...")
    annotations_source_path = os.path.join(manifest_path, f"{tablet_id}-annotator-annotations.json")
    sign_data_list = []
    if os.path.exists(annotations_source_path):
        sign_data_list = cuneur.parse_cuneur_annotations(annotations_source_path)
    else:
        print(f"- No sign annotations found at {annotations_source_path}")

    # add missing atf word index to sign annotations
    print("- Add missing word indexes to sign annotations ...")
    if transliteration_text:           
        try:
            atf_reader.set_text(transliteration_text)

            for annotation in sign_data_list:
                if 'word_index' not in annotation:
                    char_info = atf_reader.get_char_info(annotation['side'], annotation['line_index'], annotation['char_index'])
                    if char_info:
                        annotation['word_index'] = char_info['word_index']
                    else:
                        print(f"Warning: no char info for {annotation['side']} {annotation['line_index']} {annotation['char_index']}")

        except Exception:
            print(f"- Could not parse {transliteration_path}")
            continue

    # create resource images
    image_resource_items: list[AnnotationBody] = [create_image_resource_item(image, iiif_uri, _config) for image in images]

    # init manifest
    manifest_id = _config["manifest_id_prefix"] + iiif_uri.id_from_path(manifest_path + '/')
    manifest_uri = iiif_uri.create_manifest_uri(manifest_id)
    manifest_label = os.path.basename(manifest_path)
    print(f"Creating manifest: {manifest_id}")
   
    manifest = Manifest(
        id=manifest_uri, # type: ignore
        label={"en": [manifest_label]}, # type: ignore
        items=[],
        **{
            "@context": None
        }
    )
        
    # add thumbnail
    if image_resource_items[0].service:
        thumbnail_id = str(image_resource_items[0].service[0].id) + "/full/200,/0/default.jpg" # type: ignore
        thumbnail_resource = AnnotationBody(id=thumbnail_id, type="Image", width=100, height=50, format="image/jpeg") # type: ignore
        thumbnail_resource.service = image_resource_items[0].service

        manifest.thumbnail = [ thumbnail_resource ] # type: ignore

    # add metadata
    if len(nodegoat_data):
        metadata = nodegoat_to_iiif_metadata(nodegoat_data)
        manifest.metadata = metadata # type: ignore

    # choice? create single canvas, annotationpage, annotation with body choice target canvas, annotation contains image resource items
    canvases: list[Canvas] = []

    # add single canvas with choice
    # use manifest label as canvas label
    canvas_id = '0001'
    canvas = create_canvas_with_choice(canvas_id, str(manifest.label), manifest_id, image_resource_items, iiif_uri)   
    canvases.append(canvas)
    canvas_uri = canvas.id
    
    # Initialize annotations list if None
    if canvas.annotations is None:
        canvas.annotations = []

    # add translation
    if translation_text:

        # create annotation
        annotation_uri = iiif_uri.create_manifest_annotation_uri(manifest_id, f"{tablet_id}-translation.json")
        annotation_path = iiif_uri.create_manifest_annotation_path(tablet_id, f"{tablet_id}-translation.json")

        annotation = Annotation(
            id=annotation_uri, # type: ignore
            body=[
                {
                    "type": "TextualBody",
                    "value": translation_text,
                    "format": "text/plain",
                    "purpose": "translating",
                    "language": "en",
                }
            ],
            motivation="describing",
            target=[ str(canvas.id) ] # type: ignore
        )

        annotations.save_iiif_model(annotation, annotation_path) # type: ignore

        # create translation annotation page
        anno_page_uri = iiif_uri.create_manifest_annotation_page_uri(manifest_id, f"{tablet_id}-translations.json")
        anno_page_path = iiif_uri.create_manifest_annotation_page_path(tablet_id, f"{tablet_id}-translations.json")

        anno_page = annotations.create_annotation_page(anno_page_uri, "Translations", [annotation])       
        annotations.save_iiif_model(anno_page, anno_page_path) # type: ignore

        # add annotation page reference to canvas
        anno_page_ref = AnnotationPageRefExtended(id=anno_page.id, type="AnnotationPage") # type: ignore
        canvas.annotations.append(anno_page_ref)

    # add transliteration
    if transliteration_text:

        # create annotation
        annotation_uri = iiif_uri.create_manifest_annotation_uri(manifest_id, f"{tablet_id}-transliteration.json")
        annotation_path = iiif_uri.create_manifest_annotation_path(tablet_id, f"{tablet_id}-transliteration.json")

        annotation = Annotation(
            id=annotation_uri, # type: ignore
            body=[
                {
                    "type": "TextualBody",
                    "value": transliteration_text,
                    "format": "text/x-atf",
                    "purpose": "transliterating",
                }
            ],
            motivation="describing",
            target=[ str(canvas.id) ] # type: ignore
        )
        annotations.save_iiif_model(annotation, annotation_path) # type: ignore

        # create annotation page
        anno_page_uri = iiif_uri.create_manifest_annotation_page_uri(manifest_id, f"{tablet_id}-transliterations.json")
        anno_page_path = iiif_uri.create_manifest_annotation_page_path(tablet_id, f"{tablet_id}-transliterations.json")        

        anno_page = annotations.create_annotation_page(anno_page_uri, "Transliterations", [annotation])
        annotations.save_iiif_model(anno_page, anno_page_path) # type: ignore

        # add annotation page to canvas
        anno_page_ref = AnnotationPageRefExtended(id=anno_page.id, type="AnnotationPage") # type: ignore
        canvas.annotations.append(anno_page_ref)

    # add sign annotations?
    if len(sign_data_list):

        # rescale sign annotations
        scale_factor = max([canvas.width/_config['image_api']['max_width'], canvas.height/_config['image_api']['max_height']])
        if scale_factor != 1:
            for annotatation_index, annotation in enumerate(sign_data_list):
                if annotation.get('points'):
                    annotation['points'] = svg.rescale_points(annotation['points'], scale_factor) # type: ignore

        # create annotations
        items = []
        for sign in sign_data_list:
            annotation_uri = iiif_uri.create_manifest_annotation_uri(manifest_id, f"{sign['id']}.json")
            annotation_path = iiif_uri.create_manifest_annotation_path(tablet_id, f"{sign['id']}.json")

            annotation = annotations.create_sign_annotation(sign, annotation_uri, str(canvas.id))
            annotations.save_iiif_model(annotation, annotation_path) # type: ignore

            items.append(annotation)

        # create annotation page
        anno_page_uri = iiif_uri.create_manifest_annotation_page_uri(manifest_id, f"{tablet_id}-signs.json")
        anno_page_path = iiif_uri.create_manifest_annotation_page_path(tablet_id, f"{tablet_id}-signs.json")

        anno_page = annotations.create_annotation_page(anno_page_uri, "Sign Annotations", items)
        annotations.save_iiif_model(anno_page, anno_page_path) # type: ignore

        # add annotation page reference to canvas
        anno_page_ref = AnnotationPageRefExtended(id=anno_page.id, type="AnnotationPage") # type: ignore
        canvas.annotations.append(anno_page_ref)

    # add word annotations?

    # add line annotations            

    # add canvases to manifest
    manifest.items = canvases

    # add seeAlso
    data_files = [
        {
            "file": f"{tablet_id}-transliteration-atf.txt",
            "label": "Transliteration (ATF)",
            "type": "text/x-atf",
        },
        {
            "file": f"{tablet_id}-translation.txt",
            "label": "Translation",
            "type": "text/plain",
        },
        {
            "file": f"{tablet_id}-data.json",
            "label": "Metadata",
            "type": "application/json",
        },
    ]

    see_also = []
    for data_file in data_files:
        data_file_uri = iiif_uri.create_manifest_data_uri(manifest_id, data_file['file'])
        data_file_path = iiif_uri.create_manifest_data_path(tablet_id, data_file['file'])

        if os.path.exists(os.path.join(manifest_path, data_file['file'])):
            # copy file to data path
            shutil.copy2(os.path.join(manifest_path, data_file['file']), data_file_path)

        item = LinkedResource(
            id=data_file_uri, # type: ignore
            type="Dataset",
            label={"en": [data_file['label']]}, # type: ignore
            format=data_file['type'], # type: ignore
            profile="https://iiif.io/api/presentation/3/seeAlso.json"
        )
        see_also.append(item)
    manifest.seeAlso = see_also # type: ignore

    # output manifest
    annotations.save_iiif_model(manifest, os.path.join(manifest_path, 'manifest.json')) # type: ignore

    # add to collection manifest
    manifest_ref = ManifestRef(
        id=str(manifest.id), # type: ignore
        label=manifest.label,
        # **{
        #     "@context": None
        # }
    )
    manifest_ref.thumbnail = manifest.thumbnail # type: ignore
    if collection_manifest.items is None:
        collection_manifest.items = []
    collection_manifest.items.append(manifest_ref) # type: ignore


# output collection manifest
collection_manifest_uri = iiif_uri.create_collection_uri(_config['collection_id'])
collection_manifest_path = os.path.join(base_path, 'collection.json')
annotations.save_iiif_model(collection_manifest, collection_manifest_path) # type: ignore

