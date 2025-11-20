import json
from typing import Dict, Any, List


def nodegoat_to_iiif_metadata(data: Dict) -> List[Dict[str, Any]]:
    """
    Converts nodegoat export to IIIF metadata format.

    Args:
        data: Dictionary containing nodegoat export data

    Returns:
        List of metadata dictionaries in IIIF format
    """

    metadata = []

    # Period
    if data.get('period'):
        values = [
            f'<a target="_blank" href="{item["uri"]}">{item["label"]}</a>' if item.get('uri') else item['label']
            for item in data['period']
        ]
        metadata.append({
            'label': {'en': ['Period']},
            'value': {'en': values}
        })

    # Languages
    if data.get('languages'):
        values = [
            f'<a target="_blank" href="{item["uri"]}">{item["label"]}</a>' if item.get('uri') else item['label']
            for item in data['languages']
        ]
        metadata.append({
            'label': {'en': ['Languages']},
            'value': {'en': values}
        })

    # Material
    if data.get('material'):
        values = [
            f'<a target="_blank" href="{item["uri"]}">{item["label"]}</a>' if item.get('uri') else item['label']
            for item in data['material']
        ]
        metadata.append({
            'label': {'en': ['Material']},
            'value': {'en': values}
        })

    # Object Type
    if data.get('object_type'):
        values = [
            f'<a target="_blank" href="{item["uri"]}">{item["label"]}</a>' if item.get('uri') else item['label']
            for item in data['object_type']
        ]
        metadata.append({
            'label': {'en': ['Object Type']},
            'value': {'en': values}
        })

    # Genres
    if data.get('genres'):
        values = [
            f'<a target="_blank" href="{item["genre"]["uri"]}">{item["genre"]["label"]}</a>'
            if item.get('genre', {}).get('uri') else item['genre']['label']
            for item in data['genres']
        ]
        metadata.append({
            'label': {'en': ['Genres']},
            'value': {'en': values}
        })

    # External ID
    if data.get('external_id'):
        values = [
            f'<a target="_blank" href="{item["uri"]}">{item["collection"]["label"]}: {item["id"]}</a>'
            if item.get('uri') else f'{item["collection"]["label"]}: {item["id"]}'
            for item in data['external_id']
        ]
        metadata.append({
            'label': {'en': ['External ID']},
            'value': {'en': values}
        })

    # Collection
    if data.get('collection'):
        values = [
            f'<a target="_blank" href="{item["collection"]["uri"]}">{item["collection"]["label"]} : {item["number"]}</a>'
            if item.get('collection', {}).get('uri')
            else f'{item["collection"]["label"]}: {item["number"]}'
            for item in data['collection']
        ]
        metadata.append({
            'label': {'en': ['Collection']},
            'value': {'en': values}
        })

    # Publications
    if data.get('publications'):
        values = [item['reference'] for item in data['publications']]
        metadata.append({
            'label': {'en': ['Publications']},
            'value': {'en': values}
        })

    return metadata
